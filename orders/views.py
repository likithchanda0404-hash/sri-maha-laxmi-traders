from decimal import Decimal
import urllib.parse

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from catalog.models import Product
from accounts.models import CustomerProfile
from .cart import Cart
from .models import Order, OrderItem


def digits_only(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


# -----------------------------
# CART (with totals)
# -----------------------------
@login_required
def cart_detail(request):
    cart = Cart(request)
    product_ids = cart.cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = Decimal("0.00")

    for p in products:
        qty = int(cart.cart.get(str(p.id), 0))
        price = Decimal(str(p.price))
        subtotal = price * qty
        total += subtotal

        items.append({
            "product": p,
            "qty": qty,
            "price": price,
            "subtotal": subtotal,
        })

    return render(request, "orders/cart.html", {"items": items, "total": total})


@login_required
def cart_add(request, product_id):
    cart = Cart(request)
    cart.add(product_id, qty=1)
    messages.success(request, "Added to cart.")
    return redirect("cart_detail")


@login_required
def cart_update(request, product_id):
    cart = Cart(request)
    qty = request.POST.get("qty", "1")
    cart.set_qty(product_id, qty)
    messages.success(request, "Cart updated.")
    return redirect("cart_detail")


@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    messages.success(request, "Removed from cart.")
    return redirect("cart_detail")


# -----------------------------
# CHECKOUT + CREATE ORDER
# -----------------------------
@login_required
def checkout(request):
    cart = Cart(request)

    if not cart.cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart_detail")

    profile, _ = CustomerProfile.objects.get_or_create(user=request.user)

    product_ids = cart.cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    items = []
    total = Decimal("0.00")

    for p in products:
        qty = int(cart.cart.get(str(p.id), 0))
        price = Decimal(str(p.price))
        subtotal = price * qty
        total += subtotal
        items.append({"product": p, "qty": qty, "price": price, "subtotal": subtotal})

    if request.method == "POST":
        fulfillment = request.POST.get("fulfillment", "pickup")
        phone = request.POST.get("phone", "").strip()
        whatsapp = request.POST.get("whatsapp", "").strip()
        address = request.POST.get("address", "").strip()
        notes = request.POST.get("notes", "").strip()

        if not phone or not whatsapp:
            messages.error(request, "Phone and WhatsApp number are required.")
            return redirect("checkout")

        # save profile
        profile.phone = phone
        profile.address = address
        profile.save()

        order = Order.objects.create(
            user=request.user,
            fulfillment=fulfillment,
            phone=phone,
            whatsapp=whatsapp,
            address=address,
            notes=notes,
        )

        created_any_item = False

        # create items + reduce stock_quantity
        for p in products:
            requested_qty = int(cart.cart.get(str(p.id), 0))
            if requested_qty <= 0:
                continue

            available = int(p.stock_quantity)
            qty_to_add = min(requested_qty, available)

            if qty_to_add > 0:
                OrderItem.objects.create(order=order, product=p, qty=qty_to_add)
                created_any_item = True
                p.stock_quantity = available - qty_to_add
                p.save()

        cart.clear()

        if not created_any_item:
            order.delete()
            messages.error(request, "Sorry, items are out of stock. Please try again.")
            return redirect("cart_detail")

        messages.success(request, f"Order placed successfully! Order ID: {order.id}")
        return redirect("order_success", order_id=order.id)

    return render(request, "orders/checkout.html", {
        "profile": profile,
        "items": items,
        "total": total
    })


# -----------------------------
# ORDER SUCCESS (Shop WhatsApp + Invoice links)
# -----------------------------
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Shop WhatsApp message
    lines = []
    lines.append(f"New Order #{order.id}")
    lines.append(f"Customer: {order.user.username}")
    lines.append(f"Phone: {order.phone}")
    lines.append(f"Customer WhatsApp: {order.whatsapp}")
    lines.append(f"Fulfillment: {order.get_fulfillment_display()}")

    if order.address:
        lines.append(f"Address: {order.address}")
    if order.notes:
        lines.append(f"Notes: {order.notes}")

    lines.append("")
    lines.append("Items:")
    for item in order.items.all():
        lines.append(f"- {item.product.name} × {item.qty}")

    lines.append("")
    lines.append("Please confirm this order.")

    message = "\n".join(lines)
    shop_url = f"https://wa.me/{digits_only(settings.WHATSAPP_ORDER_NUMBER)}?text={urllib.parse.quote(message)}"

    return render(request, "orders/order_success.html", {
        "order": order,
        "whatsapp_url": shop_url
    })


# -----------------------------
# INVOICE (HTML)
# -----------------------------
@login_required
def invoice_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    items = []
    total = Decimal("0.00")
    for it in order.items.all():
        price = Decimal(str(it.product.price))
        subtotal = price * it.qty
        total += subtotal
        items.append({"name": it.product.name, "qty": it.qty, "price": price, "subtotal": subtotal})

    return render(request, "orders/invoice.html", {"order": order, "items": items, "total": total})


# -----------------------------
# INVOICE PDF (Download)
# -----------------------------
@login_required
def invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    lines = []
    total = Decimal("0.00")
    for it in order.items.all():
        price = Decimal(str(it.product.price))
        subtotal = price * it.qty
        total += subtotal
        lines.append((it.product.name, it.qty, str(price), str(subtotal)))

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_order_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 60
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Sri Maha Laxmi Traders")

    y -= 18
    p.setFont("Helvetica", 10)
    p.drawString(50, y, "6-8-151, Namdevada, Nizamabad 503002, Telangana")
    y -= 14
    p.drawString(50, y, "Phone: +91 9440574394, +91 7386034104")
    y -= 14
    p.drawString(50, y, "Email: santhoshchanda4@gmail.com, likith.chanda0404@gmail.com")

    y -= 26
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"INVOICE - Order #{order.id}")
    y -= 16

    p.setFont("Helvetica", 10)
    p.drawString(50, y, f"Customer: {order.user.username}")
    y -= 14
    p.drawString(50, y, f"Phone: {order.phone}   WhatsApp: {order.whatsapp}")
    y -= 14
    p.drawString(50, y, f"Fulfillment: {order.get_fulfillment_display()}   Status: {order.status}")
    y -= 14

    if order.address:
        p.drawString(50, y, f"Address: {order.address[:90]}")
        y -= 14

    y -= 10
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Item")
    p.drawString(300, y, "Qty")
    p.drawString(350, y, "Price")
    p.drawString(430, y, "Subtotal")

    y -= 10
    p.line(50, y, 545, y)
    y -= 14

    p.setFont("Helvetica", 10)
    for name, qty, price, subtotal in lines:
        if y < 80:
            p.showPage()
            y = height - 60
            p.setFont("Helvetica", 10)

        p.drawString(50, y, name[:38])
        p.drawString(300, y, str(qty))
        p.drawString(350, y, f"₹ {price}")
        p.drawString(430, y, f"₹ {subtotal}")
        y -= 14

    y -= 10
    p.line(50, y, 545, y)
    y -= 18

    p.setFont("Helvetica-Bold", 12)
    p.drawString(350, y, f"TOTAL: ₹ {total}")

    y -= 28
    p.setFont("Helvetica", 10)
    p.drawString(50, y, "Thank you for shopping with Sri Maha Laxmi Traders!")

    p.showPage()
    p.save()
    return response
