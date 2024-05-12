# Generated by Django 5.0.4 on 2024-05-11 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0007_remove_productinput_all_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='productinput',
            name='input_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='productoutput',
            name='all_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
        migrations.AlterField(
            model_name='productoutput',
            name='output_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
