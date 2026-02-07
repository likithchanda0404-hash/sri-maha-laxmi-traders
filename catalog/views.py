from django.shortcuts import render, get_object_or_404
from .models import Brand, Product

def brand_list(request):
    brands = Brand.objects.filter(is_active=True)
    return render(request, "catalog/brand_list.html", {"brands": brands})

def products_by_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id, is_active=True)
    products = Product.objects.filter(is_active=True, brand=brand).select_related("brand", "category")
    return render(request, "catalog/products_by_brand.html", {"brand": brand, "products": products})

def product_list(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True).select_related("brand", "category")
    if q:
        products = products.filter(name__icontains=q)
    return render(request, "catalog/product_list.html", {"products": products, "q": q})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, "catalog/product_detail.html", {"product": product})
