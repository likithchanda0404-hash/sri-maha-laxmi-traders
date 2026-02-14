from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, Brand


def product_list(request):
    """
    DEBUG-SAFE products page:
    - Does not use templates
    - Will never show a blank 500
    - If something fails, it prints the exact error on screen
    """
    try:
        q = (request.GET.get("q") or "").strip()

        qs = Product.objects.all()

        # optional: filter is_active if it exists
        if hasattr(Product, "is_active"):
            qs = qs.filter(is_active=True)

        if q:
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(brand__name__icontains=q)
                | Q(category__name__icontains=q)
            )

        qs = qs[:100]

        if not qs:
            return HttpResponse("No products found (Render DB may be empty).")

        lines = []
        for p in qs:
            # safe access for fields
            stock = getattr(p, "stock_quantity", None)
            price = getattr(p, "price", None)
            brand = getattr(p, "brand", None)
            brand_name = getattr(brand, "name", "-") if brand else "-"
            lines.append(f"{p.id} | {p.name} | brand={brand_name} | price={price} | stock={stock}")

        return HttpResponse("<br>".join(lines))

    except Exception as e:
        return HttpResponse(f"PRODUCTS ERROR: {type(e).__name__}: {e}", status=500)


def brand_list(request):
    """
    Keep normal view (uses template)
    """
    brands = Brand.objects.all()
    if hasattr(Brand, "is_active"):
        brands = brands.filter(is_active=True)

    return render(request, "catalog/brand_list.html", {"brands": brands})


def products_by_brand(request, brand_id):
    """
    Keep normal view (uses template)
    """
    brand = get_object_or_404(Brand, id=brand_id)
    products = Product.objects.filter(brand=brand)
    if hasattr(Product, "is_active"):
        products = products.filter(is_active=True)

    return render(request, "catalog/products_by_brand.html", {
        "brand": brand,
        "products": products,
    })


def product_detail(request, product_id):
    """
    Keep normal view (uses template)
    """
    product = get_object_or_404(Product, id=product_id)
    return render(request, "catalog/product_detail.html", {"product": product})
