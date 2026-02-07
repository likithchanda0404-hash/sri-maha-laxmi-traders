from django.contrib import admin
from django.utils.html import format_html
import urllib.parse

from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "fulfillment", "status", "created_at", "send_delivered_whatsapp")
    list_filter = ("status", "fulfillment", "created_at")
    search_fields = ("user__username", "phone", "whatsapp")
    inlines = [OrderItemInline]

    actions = ["mark_confirmed", "mark_packed", "mark_out_for_delivery", "mark_delivered", "mark_cancelled"]

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.update(status="Confirmed")

    @admin.action(description="Mark selected orders as Packed")
    def mark_packed(self, request, queryset):
        queryset.update(status="Packed")

    @admin.action(description="Mark selected orders as Out for Delivery")
    def mark_out_for_delivery(self, request, queryset):
        queryset.update(status="Out for Delivery")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.update(status="Delivered")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        queryset.update(status="Cancelled")

    def send_delivered_whatsapp(self, obj):
        if not obj.whatsapp:
            return "-"

        msg = f"Hi! Your order #{obj.id} from Sri Maha Laxmi Traders has been Delivered ✅. Thank you!"
        url = f"https://wa.me/{self._digits_only(obj.whatsapp)}?text={urllib.parse.quote(msg)}"
        return format_html('<a href="{}" target="_blank">Send Delivered</a>', url)

    send_delivered_whatsapp.short_description = "WhatsApp"

    def _digits_only(self, s: str) -> str:
        return "".join(ch for ch in s if ch.isdigit())

admin.site.register(OrderItem)
