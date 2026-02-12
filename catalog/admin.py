from django.contrib import admin
from .models import Brand, Category, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "telugu_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

    def telugu_name(self, obj):
        # Safe even if the field doesn't exist in production
        val = getattr(obj, "name_te", "") or ""
        return val if val.strip() else "-"
    telugu_name.short_description = "Name (TE)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "telugu_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

    def telugu_name(self, obj):
        val = getattr(obj, "name_te", "") or ""
        return val if val.strip() else "-"
    telugu_name.short_description = "Name (TE)"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "brand", "category", "price", "stock_quantity", "is_active", "updated_at")
    list_filter = ("is_active", "brand", "category")
    search_fields = ("name", "brand__name", "category__name")
