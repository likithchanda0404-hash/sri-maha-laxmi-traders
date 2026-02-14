from django.shortcuts import render
from django.db.models import Q
from .models import Product


def product_list(request):
    q = (request.GET.get("q") or "").strip()

    products = Product.objects.all()

    # If your Product model has is_active, filter safely
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
