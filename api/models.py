from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


# Create your models here.


class CategoryProduct(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title


class Sale(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    salePrice = models.IntegerField(default=0)
    dateFrom = models.DateTimeField(auto_now_add=True)
    dateTo = models.DateTimeField(auto_now_add=True)


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
        self.product_reviewed.save()    # TODO почему-то не работает.
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
    reviews = models.ManyToManyField(ProductReview, blank=True)
    reviews_count = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return self.title

    def bought(self, count):
        self.bought_times += count
        self.save()

    def add_to_cart(self, count):
        self.count += count
        self.save()

    def getDescription(self):
        return f'{self.desc[:10]}...'

    def getFullDescription(self):
        return self.desc


class Cart(models.Model):
    cartUser = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        return f'Корзина пользователя {self.cartUser}'

    def add_product(self, product_id, count):
        if self.products.filter(id=product_id).exists():
            Product.objects.get(id=product_id).add_to_cart(count)
        else:
            product = Product.objects.get(id=product_id)
            product.add_to_cart(count)
            self.products.add(product)


    def delete_product(self, product_id):
        pass
