class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")

        if not cart:
            cart = self.session["cart"] = {}

        self.cart = cart

    def add(self, product_id, qty=1):
        pid = str(product_id)
        qty = int(qty)

        if pid in self.cart:
            self.cart[pid] += qty
        else:
            self.cart[pid] = qty

        self.save()

    def set_qty(self, product_id, qty):
        pid = str(product_id)

        # ✅ SAFE conversion
        try:
            qty = int(qty)
        except (ValueError, TypeError):
            qty = 0

        if qty <= 0:
            self.cart.pop(pid, None)
        else:
            self.cart[pid] = qty

        self.save()

    def remove(self, product_id):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True
