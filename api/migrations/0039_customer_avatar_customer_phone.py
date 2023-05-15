# Generated by Django 4.2.1 on 2023-05-15 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0038_alter_order_delivery_type_alter_order_payment_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='avatar',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='customer',
            name='phone',
            field=models.PositiveIntegerField(blank=True, default=99999999999, max_length=10),
        ),
    ]
