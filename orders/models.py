from django.db import models
from django.contrib.auth.models import User
from catalog.models import Product

class Order(models.Model):
    FULFILLMENT_CHOICES = [
        ("pickup", "Pickup"),
        ("delivery", "Delivery"),
        ("both", "Pickup or Delivery"),
    ]

    STATUS_CHOICES = [
        ("New", "New"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fulfillment = models.CharField(max_length=20, choices=FULFILLMENT_CHOICES, default="pickup")

    phone = models.CharField(max_length=20, blank=True)
    whatsapp = models.CharField(max_length=20, blank=True)  # customer whatsapp
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="New")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.qty}"
