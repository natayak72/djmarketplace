# Generated by Django 4.2.1 on 2023-05-07 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_product_specs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='specs',
            field=models.ManyToManyField(blank=True, to='api.productspecification'),
        ),
    ]
