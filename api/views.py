import json
import os.path
import math

from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView
from django.http import JsonResponse
from django.templatetags.static import static
from .forms import ReviewCreateForm
from .models import Product, ProductReview, Cart, CategoryProduct


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
    res = []

    for product in Product.objects.all():
        tmp = get_product_card(product)

        res.append(tmp)

    return JsonResponse(res, safe=False)


def limited_products_view(request):
    res = []

    for product in Product.objects.all():
        tmp = get_product_card(product)
        res.append(tmp)

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

        res = get_product_card(product=product)

        return JsonResponse(res, safe=False)
    else:
        pass
        """ Список товаров в корзине. """
        products_in_cart = [{
            'id': product.id,
            'images': get_product_images_list(product),
            'title': product.title,
            'price': product.price,
            'count': product.count
        } for product in Cart.objects.get(cartUser=request.user).products.all()]
        return JsonResponse(products_in_cart, safe=False)


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
            return JsonResponse(reviews, safe=False)
        else:
            # На фронтенде нет механизма отображения информации о неправильно введённом поле.
            # Поэтому просто возвращаем старые отзывы, без изменений.
            reviews = [{
                'author': review.author,
                'email': review.email,
                'text': review.text,
                'rate': review.rate
            } for review in ProductReview.objects.all()]
            return JsonResponse(reviews, safe=False)


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
                elif 'freeDelivery' in key:
                    # products_filter[key.split('[')[1].split(']')[0]] = False if value == 'false' else True
                    x = 1
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
        # TODO Реализовать поле "В наличии"
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
