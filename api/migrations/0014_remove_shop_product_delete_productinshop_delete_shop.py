# Generated by Django 4.2.1 on 2023-05-11 19:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_alter_productincart_product'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shop',
            name='product',
        ),
        migrations.DeleteModel(
            name='ProductInShop',
        ),
        migrations.DeleteModel(
            name='Shop',
        ),
    ]