# Generated by Django 4.2.1 on 2023-05-13 19:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0035_alter_order_address_alter_order_city_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
    ]
