from django.contrib import admin
from .models import Brand, Category, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "name_te", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "name_te")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "name_te", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "name_te")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "price", "stock_quantity", "is_active")
    list_filter = ("brand", "category", "is_active")
    search_fields = ("name", "name_te", "brand__name", "category__name")
    list_editable = ("price", "stock_quantity", "is_active")
