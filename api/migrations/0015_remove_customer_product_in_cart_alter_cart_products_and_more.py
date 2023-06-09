# Generated by Django 4.2.1 on 2023-05-11 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_remove_shop_product_delete_productinshop_delete_shop'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='product_in_cart',
        ),
        migrations.AlterField(
            model_name='cart',
            name='products',
            field=models.ManyToManyField(blank=True, to='api.product'),
        ),
        migrations.DeleteModel(
            name='ProductInCart',
        ),
    ]
