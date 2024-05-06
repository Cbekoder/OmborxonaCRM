from django.contrib import admin
from .models import Category, Unit, Product, ProductInput, ProductOutput

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'quantity', 'unit', 'prod_code')
    list_filter = ('category', 'unit',)
    search_fields = ('name', 'prod_code',)

@admin.register(ProductInput)
class ProductInputAdmin(admin.ModelAdmin):
    list_display = ('product', 'input_quantity', 'created_at', 'user_id')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'user_id__username')

@admin.register(ProductOutput)
class ProductOutputAdmin(admin.ModelAdmin):
    list_display = ('product', 'output_quantity', 'created_at', 'user_id')
    list_filter = ('created_at',)
    search_fields = ('product__name', 'user_id__username')
