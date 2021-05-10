# 신발 리셀 중개사이트 shockX

> ### 패션아이템 리셀 중개 사이트 <a href="https://stockx.com/">stockX</a>를 모티브로 한 프로젝트입니다.

👇 아래 이미지를 클릭하시면 시연 영상이 재생됩니다.
[![shockX](https://user-images.githubusercontent.com/67499510/117602700-4a003f00-b18c-11eb-8982-853a828f6672.png)](https://youtu.be/4yEd7uMqjMc)

### 개발일정
- 기간 : 2021.03.02 - 2021.03.12 (11일)
- 구성원 : 프론트 3명, 백엔드 4명

### 기술 스택
- Language: Python
- Framework: Django
- Database: MySQL
- AWS(EC2, RDS)
- Bcrypt, JWT, 카카오 소셜 로그인 API

### 협업 도구
- Git, Github
- Trello : 일정 관리
- Notion : API 문서 작성
- Slack : 비대면 소통

### 담당 구현 기능
- 관계형 데이터베이스 모델링, **AWS RDS** 연동
- 경매 방식의 거래 API 구현
- 원자성 확보를 위해 **트랜잭션** 단위로 DB 업데이트
- Prefetch 객체, annotate 메소드를 적용한 **쿼리 최적화**
- 파이썬 unittest 모듈을 활용한 **유닛테스트**
- **Docker**를 통한 AWS EC2 배포
- **git rebase**를 활용한 commit log 관리

### 백엔드 구현 기능
모델링
- 관계형 데이터베이스 모델링
- 데이터 csv 파일 작성, 데이터 업로더 작성

회원가입 & 로그인(User)
- 카카오 소셜 로그인
- 로그인 데코레이터를 통한 토큰 인증

상품(Product)
- 상품 리스트페이지 조회(조건별 필터링)
- 상품 상세페이지 조회(사이즈별 통계 정보 제공)

주문(Order)
- 경매 방식의 상품 구매, 판매 시스템 구현
- 마이페이지 구매, 판매 내역 조회
- 포트폴리오 상품 등록, 조회

유닛테스트
- 엔드포인트별 유닛테스트 진행

# Reference
- 이 프로젝트는 <a href="https://stockx.com/">stockX</a> 사이트를 참조하여 학습목적으로 만들었습니다.
- 실무수준의 프로젝트이지만 학습용으로 만들었기 때문에 이 코드를 활용하여 이득을 취하거나 무단 배포할 경우 법적으로 문제될 수 있습니다.
- 이 프로젝트에서 사용하고 있는 사진 대부분은 위코드에서 구매한 것이므로 해당 프로젝트 외부인이 사용할 수 없습니다.
