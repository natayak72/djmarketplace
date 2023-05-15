from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# Create your models here.


class CategoryProduct(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    subcategory = models.ManyToManyField('CategoryProduct', blank=True)

    def __str__(self):
        return self.title


class Sale(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    salePrice = models.IntegerField(default=0)
    dateFrom = models.DateTimeField(auto_now_add=True)
    dateTo = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title


class Customer(models.Model):
    customerUser = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    # 0-100 - Покупатель
    # 100-200 - Постоянный покупатель
    # 300 - ... - Уважаемый покупатель
    status = models.CharField(max_length=100, default='Покупатель')
    buy_summ = models.PositiveIntegerField(default=0)
    phone = models.PositiveIntegerField(default=99999999999, blank=True)
    avatar = models.FileField(upload_to='api/static/avatar', blank=True)

    def __str__(self):
        return self.customerUser.username

    def top_up_balance(self, top_up_summ):
        self.balance += float(top_up_summ)

    def cart_pay(self):
        for product in Cart.objects.all():
            product_summ = product.get_product_sum()
            self.balance -= product_summ
            self.buy_summ += product_summ

            products_bought_count = product.get_count()
            product_item = product.product.product
            product_item.bought(products_bought_count)

            product.delete()

        if 100 < self.buy_summ <= 200:
            self.status = 'Постоянный покупатель'
        else:
            self.status = 'Уважаемый покупатель'

        self.save()


class ProductReview(models.Model):
    product_reviewed = models.ForeignKey('Product', on_delete=models.DO_NOTHING)
    author = models.CharField(max_length=50)
    email = models.EmailField(blank=True)
    rate = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=500)

    def __str__(self):
        return f'{self.author} о {self.product_reviewed}: {self.text[:20]}...'

    def delete(self, using=None, keep_parents=False):
        self.product_reviewed.reviews_count -= 1
        self.product_reviewed.save()  # TODO почему-то не работает.
        super(ProductReview, self).delete()


spec_types = [('weight', 'Масса'),
              ('volume', 'Объем'),
              ('items', 'Штук')
              ]


class ProductSpecification(models.Model):
    name = models.CharField(max_length=100, choices=spec_types)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} - {self.value}'


class Product(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    price = models.FloatField(default=0)
    count = models.IntegerField(default=0)  # Число товара в корзине
    bought_times = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0)
    category = models.ForeignKey(CategoryProduct, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)
    desc = models.TextField(max_length=3000, null=True)
    specs = models.ManyToManyField(ProductSpecification, blank=True)
    delivery = models.BooleanField(default=False)
    available = models.BooleanField(default=True)
    reviews = models.ManyToManyField(ProductReview, blank=True)
    reviews_count = models.IntegerField(default=0, blank=True)
    limited = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def bought(self, count):
        self.bought_times += count
        self.save()

    def add_to_cart(self, count):
        self.count += count
        self.save()

    def getDescription(self):
        return f'{self.desc[:30]}...'

    def getFullDescription(self):
        return self.desc


class Cart(models.Model):
    cartUser = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f'Корзина пользователя {self.cartUser}'

    def add_product(self, product_id, count):
        # 1. Продукт уже есть в корзине. Добавляем нужное количество
        if self.products.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)
            product.add_to_cart(count)

        # Продукта нет в корзине. Добавляем нужное количество
        else:
            product = Product.objects.get(id=product_id)
            product.add_to_cart(count)
            self.products.add(product)

    def delete_product(self, product_id):
        pass


delivery_types = [('ordinary', 'Доставка'),
                  ('express', 'Экспресс-доставка'),
                  ]

payment_types = [('online', 'Онлайн картой'),
                 ('someone', 'Онлайн со случайного чужого счёта'),
                 ]

statuses = [('not_paid', 'Не оплачен'),
            ('paid', 'Оплачен'),
            ('pay_error', 'Ошибка оплаты'),
            ]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    creationDate = models.DateTimeField(auto_now_add=True)
    # Маска подстановки - +7() ___ - __ - __, храниться должно в виде 10 цифр без кода страны
    phone = models.CharField(max_length=20, help_text='Номер телефона', blank=True)  # TODO валидация
    delivery_type = models.CharField(choices=delivery_types, max_length=100, blank=True)
    city = models.CharField(max_length=100, help_text='Город доставки', blank=True)
    address = models.CharField(max_length=500, help_text='Адрес доставки', blank=True)
    payment_types = models.CharField(choices=payment_types, max_length=100, blank=True)
    status = models.CharField(choices=statuses, max_length=100, blank=True)
    total_cost = models.FloatField(default=0, help_text='Общая стоимость товаров в заказе', blank=True)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f'Заказ от {self.user} на {self.total_cost}'


