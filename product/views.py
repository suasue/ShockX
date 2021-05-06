import json

from django.views     import View
from django.http      import JsonResponse
from django.db.models import Q, Min, Avg, Prefetch, Case, When

from product.models import Product, Size, ProductSize
from order.models   import Ask, Bid

ORDER_STATUS_CURRENT = 'current'
ORDER_STATUS_HISTORY = 'history'

class ProductListView(View):
    def get(self, request):
        lowest_price  = request.GET.get('lowest', None)
        highest_price = request.GET.get('highest', None)
        size          = int(request.GET.get('size', 0))
        limit         = int(request.GET.get('limit', 0))
        offset        = int(request.GET.get('offset', 0))
        
        product_condition = Q(productsize__ask__order_status__name=ORDER_STATUS_CURRENT)

        if lowest_price:
            product_condition.add(Q(min_price__gte=lowest_price), Q.AND)

        if highest_price:
            product_condition.add(Q(min_price__lte=highest_price), Q.AND)

        if size:
            product_condition.add(Q(productsize__size_id=size), Q.AND)

        products = Product.objects.prefetch_related('image_set').annotate(min_price=Min('productsize__ask__price')).filter(product_condition)

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

        return JsonResponse({'products':total_products, 'size_categories':size_categories}, status=200)

class ProductDetailView(View):
    def get(self, request, product_id):
        if not ProductSize.objects.filter(product_id=product_id).exists():
            return JsonResponse({'message':'PRODUCT_DOES_NOT_EXIST'}, status=404)

        product       = Product.objects.prefetch_related('image_set').get(id=product_id)
        product_sizes = ProductSize.objects.select_related('size')\
            .filter(product_id=product_id)\
            .prefetch_related('product__image_set', 
                Prefetch('ask_set', queryset=Ask.objects.filter(order_status__name=ORDER_STATUS_CURRENT).order_by('price'), to_attr='lowest_ask'),
                Prefetch('bid_set', queryset=Bid.objects.filter(order_status__name=ORDER_STATUS_CURRENT).order_by('-price'), to_attr='highest_bid'),
                Prefetch('ask_set', queryset=Ask.objects.filter(order_status__name=ORDER_STATUS_HISTORY).order_by('-matched_at'), to_attr='ask_history'),
            ).annotate(total_avg=Avg(
                Case(
                    When(
                        ask__order_status__name=ORDER_STATUS_HISTORY,
                        then='ask__price'
                    )
                )
            ))

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
            'size_name'               : product_size.size.name,
            'last_sale'               : int(product_size.ask_history[0].price) if product_size.ask_history else 0,
            'price_change'            : int(product_size.ask_history[0].price - product_size.ask_history[1].price) if product_size.ask_history else 0,
            'price_change_percentage' : int((product_size.ask_history[0].price - product_size.ask_history[1].price) / product_size.ask_history[1].price * 100)\
                                        if product_size.ask_history else 0,
            'lowest_ask'              : int(product_size.lowest_ask[0].price) if product_size.lowest_ask else 0,
            'highest_bid'             : int(product_size.highest_bid[0].price) if product_size.highest_bid else 0,
            'total_sales'             : len(product_size.ask_history),
            'price_premium'           : int((product_size.ask_history[0].price - product.retail_price) / product.retail_price * 100) if product_size.ask_history else 0,
            'average_sale_price'      : int(product_size.total_avg) if product_size.total_avg else 0,
            'sales_history': [{
                'sale_price'     : int(ask.price),
                'date_time'      : ask.matched_at.strftime('%Y-%m-%d'),
                'time'           : ask.matched_at.strftime('%H:%m')
                } for ask in product_size.ask_history
            ]
            } for product_size in product_sizes
        ]

        return JsonResponse({'results':results}, status=200)
