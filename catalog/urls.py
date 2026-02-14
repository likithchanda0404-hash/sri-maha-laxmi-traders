from django.urls import path
from . import views

urlpatterns = [
    # Brands
    path("brands/", views.brand_list, name="brand_list"),
    path("brand/<int:brand_id>/", views.products_by_brand, name="products_by_brand"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
]
