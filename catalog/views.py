from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Brand


def product_list(request):
    q = (request.GET.get("q") or "").strip()

    products = Product.objects.all()

    # safe filter if your Product has is_active
    if hasattr(Product, "is_active"):
        products = products.filter(is_active=True)

    if q:
        products = products.filter(
            Q(name__icontains=q)
            | Q(brand__name__icontains=q)
            | Q(category__name__icontains=q)
        )

    return render(request, "catalog/product_list.html", {
        "products": products,
        "q": q,
    })


def brand_list(request):
    brands = Brand.objects.all()

    if hasattr(Brand, "is_active"):
        brands = brands.filter(is_active=True)

    return render(request, "catalog/brand_list.html", {
        "brands": brands
    })


def products_by_brand(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)

    products = Product.objects.filter(brand=brand)

    if hasattr(Product, "is_active"):
        products = products.filter(is_active=True)

    return render(request, "catalog/products_by_brand.html", {
        "brand": brand,
        "products": products,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "catalog/product_detail.html", {"product": product})
