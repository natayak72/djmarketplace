# Generated by Django 4.2.1 on 2023-05-15 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0044_alter_customer_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='limited',
            field=models.BooleanField(default=False),
        ),
    ]
