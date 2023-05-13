from django.contrib import admin

# Register your models here.

from .models import *

# Register your models here.
admin.site.register(CategoryProduct)
admin.site.register(Sale)
admin.site.register(Customer)
admin.site.register(ProductReview)
admin.site.register(ProductSpecification)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
