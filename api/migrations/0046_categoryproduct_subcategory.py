# Generated by Django 4.2.1 on 2023-05-15 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0045_product_limited'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryproduct',
            name='subcategory',
            field=models.ManyToManyField(to='api.categoryproduct'),
        ),
    ]
