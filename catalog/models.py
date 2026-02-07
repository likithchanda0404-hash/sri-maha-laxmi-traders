from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)          # e.g., Doms
    name_te = models.CharField(max_length=120, blank=True)        # e.g., డామ్స్ (optional)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)          # e.g., Pens
    name_te = models.CharField(max_length=120, blank=True)        # e.g., పెన్లు (optional)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")

    name = models.CharField(max_length=200)                       # English name
    name_te = models.CharField(max_length=220, blank=True)         # Telugu name

    description = models.TextField(blank=True)                     # English
    description_te = models.TextField(blank=True)                  # Telugu

    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to="products/", blank=True, null=True)  # main image
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"
