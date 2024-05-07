from django.db import models
from users.models import User

class Category(models.Model):
    class Meta:
        verbose_name = 'Kategoriya'
        verbose_name_plural = 'Kategoriyalar'
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Unit(models.Model):
    class Meta:
        verbose_name = "O'lchov"
        verbose_name_plural = "O'lchovlar"
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True)
    prod_code = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name

class ProductInput(models.Model):
    class Meta:
        verbose_name = 'Kirim'
        verbose_name_plural = 'Kirimlar'
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    input_quantity = models.PositiveIntegerField(default=0)
    all_quantity = models.PositiveIntegerField(default=0) # kirgandan keyingi qoldiq
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='product_input')
    def __str__(self):
        return self.product.name

class ProductOutput(models.Model):
    class Meta:
        verbose_name = 'Chiqim'
        verbose_name_plural = 'Chiqimlar'
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True,)
    output_quantity = models.PositiveIntegerField(default=0)
    all_quantity = models.PositiveIntegerField(default=0) # chiqqandan keyingi qoldiq
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User,
                                on_delete=models.SET_NULL,
                                null=True,
                                related_name='product_output')
    def __str__(self):
        return self.product.name



