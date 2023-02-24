from django.contrib import admin

from .models import Order, OrderProduct, Payment

# Register your models here.


class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = (
        "payment",
        "user",
        "product",
        "quantity",
        "product_price",
        "is_ordered",
    )


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "full_name",
        "phone_number",
        "email",
        "order_total",
        "status",
        "is_ordered",
    ]
    list_filer = ["status", "is_ordered"]
    search_fields = ["order_number", "first_name", "last_name", "email"]
    list_per_page = 20
    inlines = [OrderProductInLine]


admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
