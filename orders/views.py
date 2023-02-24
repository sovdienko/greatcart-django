import json
from datetime import date

from django.core.mail import EmailMessage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from carts.models import CartItem

from .forms import OrderForm
from .models import Order, OrderProduct, Payment


def payments(request):
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(
        user=request.user, is_ordered=False, order_number=body["orderID"]
    )
    # Save transaction details in db
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["paymentMethod"],
        amount_paid=order.order_total,
        status=body["status"],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move cart items to Order Products Table
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.user = request.user
        order_product.product = cart_item.product
        order_product.quantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.is_ordered = True
        order_product.save()
        order_product.variation.set(cart_item.variations.all())
        order_product.save()

        # Reduce of the Products available quantity
        order_product.product.stock -= order_product.quantity
        order_product.product.save()

    # Clear Cart
    cart_items.delete()

    # Send order received email to customer
    message = render_to_string(
        "orders/order_received_email.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    send_emal = EmailMessage("Thank you for order!", message, to=[request.user.email])

    try:
        # Daily quota limit can be exceeded
        send_emal.send()
    except Exception as ex:
        print(type(ex))

    # Send order number and transaction id back to SendData method via Json response
    data = {"order_number": order.order_number, "transID": payment.payment_id}

    return JsonResponse(data=data)


# Create your views here.
def place_order(request, total=0, quantity=0):
    current_user = request.user
    # if Cart is empty to redirect to shop
    cart_items = CartItem.objects.filter(user=current_user)
    if cart_items.count() < 1:
        return redirect("store")

    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # store all billing information in the table
            order = Order()
            order.user = current_user
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone_number = form.cleaned_data["phone_number"]
            order.email = form.cleaned_data["email"]
            order.address_line_1 = form.cleaned_data["address_line_1"]
            order.address_line_2 = form.cleaned_data["address_line_2"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.order_note = form.cleaned_data["order_note"]
            order.order_total = grand_total
            order.tax = tax
            order.ip = request.META.get("REMOTE_ADDR")
            order.save()
            # Generate Order Number
            year = int(date.today().strftime("%Y"))
            month = int(date.today().strftime("%m"))
            day = int(date.today().strftime("%d"))
            current_date = date(year=year, month=month, day=day).strftime("%Y%m%d")
            order.order_number = current_date + str(order.id)
            order.save()
            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
            }
            return render(
                request=request, template_name="orders/payments.html", context=context
            )
        else:
            return HttpResponse("Form is invalid")
    else:
        return redirect("checkout")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")
    context = {}
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        order_products = OrderProduct.objects.filter(order=order)
        payment = Payment.objects.get(payment_id=transID)
        order_subtotal = order.order_total - order.tax

        context = {
            "order": order,
            "order_products": order_products,
            "order_subtotal": order_subtotal,
            "payment": payment,
        }
        return render(request, "orders/order_complete.html", context=context)
    except (Payment.DoesNotExist, Order.DoesNotExist) as ex:
        return redirect("home")
