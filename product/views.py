import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q, Min, Avg, Prefetch

from .models          import Product, Size 
from order.models     import Ask, Bid

ORDER_STATUS_CURRENT = 'current'
ORDER_STATUS_HISTORY = 'history'

class ProductListView(View):
    def get(self, request):
        lowest_price  = request.GET.get('lowest', None)
        highest_price = request.GET.get('highest', None)
        limit         = int(request.GET.get('limit', 0))
        offset        = int(request.GET.get('offset', 0))
        size          = int(request.GET.get('size', 0))

        price_condition = Q()

        if lowest_price and highest_price:
            price_condition.add(Q(min_price__gte=lowest_price) & Q(min_price__lte=highest_price) & Q(productsize__ask__order_status__name=ORDER_STATUS_CURRENT), Q.AND)

        if lowest_price and not highest_price:
            price_condition.add(Q(min_price__lte=lowest_price) & Q(productsize__ask__order_status__name=ORDER_STATUS_CURRENT), Q.AND)

        if highest_price and not lowest_price:
            price_condition.add(Q(min_price__gte=highest_price) & Q(productsize__ask__order_status__name=ORDER_STATUS_CURRENT), Q.AND)
        
        if size:
            price_condition.add(Q(productsize__size_id=size), Q.AND)

        products = Product.objects.prefetch_related('image_set').annotate(min_price=Min('productsize__ask__price')).filter(price_condition)

        total_products = [{
            'productId'    : product.id,
            'productName'  : product.name,
            'productImage' : product.image_set.all()[0].image_url,
            'price'        : int(product.min_price) if product.min_price else 0
            } for product in products
        ][offset:offset+limit]

        size_categories = [{
            'size'     : size.id,
            'sizeName' : size.name
            } for size in Size.objects.all()
        ]

        return JsonResponse({'products': total_products, 'size_categories': size_categories}, status=200)

class ProductDetailView(View):
    def get(self, request, product_id):
        if not Product.objects.filter(id=product_id).exists():
            return JsonResponse({'message':'PRODUCT_DOES_NOT_EXIST'}, status=404)

        product       = Product.objects.get(id=product_id)
        product_sizes = product.productsize_set.all()

        results = {
            'product_id'     : product.id,
            'product_name'   : product.name,
            'product_ticker' : product.ticker_number,
            'color'          : product.color,
            'description'    : product.description,
            'retail_price'   : product.retail_price,
            'release_date'   : product.release_date.strftime('%Y-%m-%d'),
            'style'          : product.model_number,
            'image_url'      : [product_image.image_url for product_image in product.image_set.all()]
            }

        results['sizes'] = [{
            'size_id'                 : product_size.size_id,
            'size_name'               : Size.objects.get(id=product_size.size_id).name,
            'last_sale'               : int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).last().price)\
                                        if product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).exists() else 0,
            'price_change'            : int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).order_by('-matched_at')[0].price)\
                                        - int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).order_by('-matched_at')[1].price)\
                                        if product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY) else 0,
            
            'price_change_percentage' : int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).order_by('-matched_at')[0].price)\
                                        - int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).order_by('-matched_at')[1].price)\
                                        if product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY) else 0,
            'lowest_ask'              : int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_CURRENT).order_by('price').first().price)\
                                        if product_size.ask_set.filter(order_status__name=ORDER_STATUS_CURRENT) else 0,
            'highest_bid'             : int(product_size.bid_set.filter(order_status__name=ORDER_STATUS_CURRENT).order_by('-price').first().price)\
                                        if product_size.bid_set.filter(order_status__name=ORDER_STATUS_CURRENT) else 0,
            'total_sales'             : product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).count(),
            'price_premium'           : int(100 * (int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).last().price) - int(product.retail_price))\
                                        / int(product.retail_price)) if product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).last() else 0,
            'average_sale_price'      : int(product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).aggregate(total=Avg('price'))['total'])\
                                        if product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY).exists() else 0,
            'sales_history': [{
                'sale_price'     : int(ask.price),
                'date_time'      : ask.matched_at.strftime('%Y-%m-%d'),
                'time'           : ask.matched_at.strftime('%H:%m')
                } for ask in product_size.ask_set.filter(order_status__name=ORDER_STATUS_HISTORY)
            ]
            } for product_size in product_sizes
        ]

        return JsonResponse({'results': results}, status=200)
