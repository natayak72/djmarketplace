# Generated by Django 4.2.1 on 2023-05-07 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_product_specs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productspecification',
            name='product_id',
        ),
    ]