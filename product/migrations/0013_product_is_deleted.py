# Generated by Django 5.0.4 on 2024-07-08 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_productinput_all_quantity_productoutput_all_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
