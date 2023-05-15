import json
import os.path
import math

from django.conf import settings
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.templatetags.static import static
from .forms import ReviewCreateForm
from .models import Product, ProductReview, Cart, CategoryProduct, Order, Customer, Sale


# Create your views here.
def get_product_images_list(product):
    # 0. Получить слаги категории и товара
    category_slug = CategoryProduct.objects.get(id=product.category.id).slug
    product_slug = product.slug

    # 1. Получить список названий изображений
    img_static_dir = os.path.join(settings.STATIC_ROOT, 'img')
    category_img_dir = os.path.join(img_static_dir, category_slug)
    product_img_dir = os.path.join(category_img_dir, product_slug)
    products_images = os.listdir(product_img_dir)

    # 2. Присовокупить список изображений в static()
    images = [{
        'src': static(f'img/{category_slug}/{product_slug}/{img_name}'),
        'alt': f'Картинка {img_name.split(".")[0]}'
    } for img_name in products_images]

    return images


def get_category_image(category):
    category_slug = category.slug
    img_static_dir = os.path.join(settings.STATIC_ROOT, 'img')
    categories_img_dir = os.path.join(img_static_dir, 'categories')
    for category_image in os.listdir(categories_img_dir):
        if category_slug in category_image:
            return static(f'img/categories/{category_image}')

    return ''


def get_product_card(product):
    return {
        'id': product.id,
        'category': product.category.id,
        'price': product.price,
        'count': product.count,
        'date': product.date,
        'title': product.title,
        'description': product.getDescription(),
        'fullDescription': product.getFullDescription(),
        'freeDelivery': product.delivery,
        'images': get_product_images_list(product),
        'tags': [],
        'reviews': [{
            "author": review.author,
            "email": review.author,
            "text": review.text,
            "rate": review.rate,
            "date": review.date
        } for review in ProductReview.objects.filter(product_reviewed_id=product.id)],
        'specifications': [{'name': spec.name, 'value': spec.value} for spec in product.specs.all()],
        'rating': product.rating
    }


def popular_products_view(request):
    return JsonResponse([get_product_card(product) for product in Product.objects.order_by('-pk')[:8]], safe=False)


def limited_products_view(request):
    return JsonResponse([get_product_card(product) for product in Product.objects.filter(limited=True)[:16]],
                        safe=False)


def get_category_info(category):
    subcategories = []

    for subcategory in category.subcategory.all():
        subcategories.append(get_category_info(subcategory))

    return {
        'id': category.id,
        'title': category.title,
        'image': get_category_image(category),
        'subcategories': subcategories
    }


def categories_view(request):
    res = [
    ]

    for category in CategoryProduct.objects.all():
        category_info = get_category_info(category)
        res.append(category_info)
    return JsonResponse(res, safe=False)


def product_detail_view(request, *args, **kwargs):
    """
    GET -> {
      "id": 123,
      "category": 55,
      "price": 500.67,
      "count": 12,
      "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
      "title": "video card",
      "description": "description of the product",
      "fullDescription": "full description of the product",
      "freeDelivery": true,
      "images": [
        "string"
      ],
      "tags": [
        "string"
      ],
      "reviews": [
        {
          "author": "Annoying Orange",
          "email": "no-reply@mail.ru",
          "text": "rewrewrwerewrwerwerewrwerwer",
          "rate": 4,
          "date": "2023-05-05 12:12"
        }
      ],
      "specifications": [
        {
          "name": "Size",
          "value": "XL"
        }
      ],
      "rating": 4.6
    }
    """
    if request.method == "GET":
        product = Product.objects.get(id=kwargs.get('id'))
        res = get_product_card(product)

        return JsonResponse(res, safe=False)


def basket_view(request):
    if request.method == 'POST':
        params = json.loads(request.body.decode('utf-8'))
        product_id = params.get('id')
        product = Product.objects.get(id=product_id)
        count = int(params.get('count'))

        # [0] - сам объект [1] - bool: создан объект (true) или взят уже существующий (false)
        cart = Cart.objects.get_or_create(cartUser=request.user)[0]
        cart.add_product(product.id, count)

        res = [get_product_card(product) for product in cart.products.all()]

        return JsonResponse(res, safe=False)
    elif request.method == 'GET':
        pass
        """ Список товаров в корзине. """
        products_in_cart = [{
            'id': product.id,
            'images': get_product_images_list(product),
            'title': product.title,
            'price': product.price,
            'count': product.count,
            'description': product.getDescription()
        } for product in Cart.objects.get(cartUser=request.user).products.all()]
        return JsonResponse(products_in_cart, safe=False)
    elif request.method == 'DELETE':
        params = json.loads(request.body.decode('utf-8'))
        count = params.get('count')
        product = Product.objects.get(pk=params.get('id'))
        cart = Cart.objects.get(cartUser=request.user)

        # 1. Уменьшить число count
        if count >= product.count:
            product.count = 0
            product.save()
            cart.products.remove(product)
        else:
            product.count -= count
            product.save()

        res = [get_product_card(product) for product in cart.products.all()]
        return JsonResponse(res, safe=False)


def product_reviews_view(request, product_id):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        review_form = ReviewCreateForm(data)

        if review_form.is_valid():
            clean_data = review_form.cleaned_data

            review = ProductReview.objects.create(
                product_reviewed=Product.objects.get(id=product_id),
                author=clean_data.get('author'),
                email=clean_data.get('email'),
                rate=clean_data.get('rate'),
                text=clean_data.get('text')
            )

            product_reviewed = Product.objects.get(id=product_id)
            product_reviewed.reviews.add(review)
            product_reviewed.reviews_count += 1

            product_reviewed.save()

            reviews = [{
                'author': review.author,
                'email': review.email,
                'text': review.text,
                'rate': review.rate
            } for review in ProductReview.objects.filter(product_reviewed=Product.objects.get(id=product_id))]

            res = {
                'reviews': reviews,
                'errors': None
            }

            return JsonResponse(res, safe=False)
        else:
            errors = []
            for s in review_form.errors:
                errors.append({s: review_form.errors[s]})
            reviews = [{
                'author': review.author,
                'email': review.email,
                'text': review.text,
                'rate': review.rate
            } for review in ProductReview.objects.filter(product_reviewed=Product.objects.get(id=product_id))]

            res = {
                'reviews': reviews,
                'errors': errors,
                'cleaned_data': review_form.cleaned_data
            }

            return JsonResponse(res, safe=False)


def get_sorted_products(sort_type, sort, products_list):
    if sort == 'price':
        if sort_type == 'inc':
            return [get_product_card(product) for product in
                    products_list.order_by('price')]
        elif sort_type == 'dec':
            return [get_product_card(product) for product in
                    products_list.order_by('-price')]
    elif sort == 'rating':
        if sort_type == 'inc':
            return [get_product_card(product) for product in
                    products_list.order_by('rating')]
        elif sort_type == 'dec':
            return [get_product_card(product) for product in
                    products_list.order_by('-rating')]
    elif sort == 'date':
        if sort_type == 'inc':
            return [get_product_card(product) for product in
                    products_list.order_by('date')]
        elif sort_type == 'dec':
            return [get_product_card(product) for product in
                    products_list.order_by('-date')]
    elif sort == 'reviews':
        if sort_type == 'inc':
            return [get_product_card(product) for product in
                    products_list.order_by('reviews_count')]
        elif sort_type == 'dec':
            return [get_product_card(product) for product in
                    products_list.order_by('-reviews_count')]


def catalog_view(request):
    """
    GET -> {
              "items": [
                {
                  "id": 123,
                  "category": 55,
                  "price": 500.67,
                  "count": 12,
                  "date": "Thu Feb 09 2023 21:39:52 GMT+0100 (Central European Standard Time)",
                  "title": "video card",
                  "description": "description of the product",
                  "freeDelivery": true,
                  "images": [
                    {
                      "src": "/3.png",
                      "alt": "Image alt string"
                    }
                  ],
                  "tags": [
                    {
                      "id": 12,
                      "name": "Gaming"
                    }
                  ],
                  "reviews": 5,
                  "rating": 4.6
                }
              ],
              "currentPage": 5,
              "lastPage": 10
            }
    """
    if request.method == 'GET':
        products_filter = {}
        for key, value in request.GET.items():
            if 'filter' in key:
                if 'minPrice' in key or 'maxPrice' in key:
                    products_filter[key.split('[')[1].split(']')[0]] = float(value)
                elif 'freeDelivery' in key or 'available' in key:
                    if value == 'false':
                        products_filter[key.split('[')[1].split(']')[0]] = False
                    else:
                        products_filter[key.split('[')[1].split(']')[0]] = True
                else:
                    products_filter[key.split('[')[1].split(']')[0]] = value

        current_page = int(request.GET.get('currentPage'))
        category = request.GET.get('category')
        sort = request.GET.get('sort')  # rating, price, reviews, date
        sort_type = request.GET.get('sortType')  # dec, inc
        limit = int(request.GET.get('limit'))

        # 1. Отфильтровать товары.
        products_list = Product.objects.all()
        # когда available=false, хочу, чтоб не фильтровалось по этому полю
        # Чтобы выводились не только продукты "в наличии", но и те, которых нету
        if products_filter.get('available'):
            filtered_list = products_list.filter(price__gte=products_filter.get('minPrice'),
                                                 price__lt=products_filter.get('maxPrice'),
                                                 delivery__exact=products_filter.get('freeDelivery'),
                                                 available__exact=products_filter.get('available')
                                                 )
        else:
            filtered_list = products_list.filter(price__gte=products_filter.get('minPrice'),
                                                 price__lt=products_filter.get('maxPrice'),
                                                 delivery__exact=products_filter.get('freeDelivery'))

        # 2. Разделить отфильтрованный список по страницам
        start = (current_page - 1) * limit
        end = start + limit
        last_page = math.ceil(len(filtered_list) / limit)

        # 3. Отсортировать отфильтрованный список
        sorted_list = get_sorted_products(sort_type, sort, filtered_list)

        # 4. Разбить список постранично
        sorted_list = sorted_list[start:end]

        # 5. Подготовить результаты

        res = {'currentPage': current_page, 'lastPage': last_page, 'items': sorted_list}

        return JsonResponse(res, safe=False)


def orders_view(request):
    print('orders_view')
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        new_order = Order.objects.create(user=request.user)

        for product in data:
            product_to_add_id = product.get('id')
            product_to_add = Product.objects.get(pk=product_to_add_id)
            new_order.products.add(product_to_add)
            new_order.total_cost += product_to_add.price * product_to_add.count

            new_order.save()
        return JsonResponse({'orderId': new_order.pk})

    elif request.method == 'GET':
        return JsonResponse([prepare_json_order(order) for order in Order.objects.filter(user=request.user)],
                            safe=False)


def prepare_json_order(order):
    return {'id': order.id,
            'createdAt': order.creationDate,
            'fullName': order.user.username,
            'email': order.user.email,
            'totalCost': order.total_cost,
            'products': [get_product_card(product) for product in order.products.all()]}


def specific_order_view(request, order_id):
    print('specific_order_view')
    if request.method == 'GET':
        order = Order.objects.get(pk=order_id)
        res = prepare_json_order(order)

        return JsonResponse(res, safe=False)

    elif request.method == 'POST':
        # Сохранить заказ
        data = json.loads(request.body.decode('utf-8'))

        order = Order.objects.get(pk=order_id)

        try:
            order.phone = int(data.get('phone'))
        except ValueError:
            order.phone = 9999999999

        order.delivery_type = data.get('deliveryType')
        order.city = data.get('city')
        order.address = data.get('address')
        order.payment_types = data.get('paymentType')

        order.save()

        return JsonResponse({'orderId': order_id}, safe=False)


def payment_view(request, order_id):
    if request.method == 'POST':
        return JsonResponse({}, safe=False)


def profile_view(request):
    if request.method == 'GET':
        customer = Customer.objects.get(customerUser=request.user)
        full_name = customer.customerUser.username
        email = customer.customerUser.email
        phone = customer.phone
        avatar = {'src': customer.avatar.path, 'alt': 'Аватар'}

        res = {'fullName': full_name,
               'email': email,
               'phone': phone,
               'avatar': avatar}

        return JsonResponse(res, safe=False)


def avatar_view(request):
    customer = Customer.objects.get(customerUser=request.user)
    if request.FILES:
        for filename, file in request.FILES.items():
            if file.size < 2 * 1024 * 1024:
                pass
                customer.avatar = file
                customer.save()

        return JsonResponse({'src': customer.avatar.path, 'alt': 'Аватар'}, safe=False)


def password_view(request):
    params = json.loads(request.body.decode('utf-8'))
    # Поменять пароль у пользователя
    # Где новый пароль?


def get_sale_image(sale):
    sale_slug = sale.slug
    img_static_dir = os.path.join(settings.STATIC_ROOT, 'img')
    sales_img_dir = os.path.join(img_static_dir, 'sales')
    for sale_image in os.listdir(sales_img_dir):
        if sale_slug in sale_image:
            return static(f'img/sales/{sale_image}')

    return ''


def sales_view(request):
    # 1. Получить все скидки, выбрать скидки нужной страницы
    current_page = int(request.GET.get('currentPage'))
    limit = 10  # 10 скидок на странице
    start = (current_page - 1) * limit
    end = start + limit

    filtered_list = Sale.objects.all()[start:end]

    # 2. Посчитать последнюю страницу
    last_page = math.ceil(len(filtered_list) / limit)

    # 3. отправить
    res = {
        'items': [],
        'current_page': current_page,
        'last_page': last_page
    }

    for sale in filtered_list:
        res['items'].append({
            'id': sale.product.pk,
            'price': sale.product.price,
            'salePrice': sale.salePrice,
            'dateFrom': sale.dateFrom,
            'dateTo': sale.dateTo,
            'title': sale.title,
            'images': [{'src': get_sale_image(sale), 'alt': 'Фотография скидки'}]
        })

    return JsonResponse(res, safe=False)


def sign_out_view(request):
    logout(request)


def sign_in_view(request):
    params = json.loads(request.body.decode('utf-8'))
    username = params.get('username')
    password = params.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

    return JsonResponse({}, safe=True)


def sign_up_view(request):
    params = json.loads(request.body.decode('utf-8'))
    name = params.get('name')
    username = params.get('username')
    password = params.get('password')

    user = User.objects.create_user(username=username, password=password)
    user.save()

    login(request, user)

    return JsonResponse({}, safe=True)

