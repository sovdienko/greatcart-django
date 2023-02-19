from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Product, Variation

from .models import Cart, CartItem


# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def _get_cart_item(request, product_id, cart_item_id):
    cart = Cart.objects.get(cart_id=_cart_id(request=request))
    product = get_object_or_404(Product, id=product_id)
    return CartItem.objects.get(product=product, cart=cart, id=cart_item_id)


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # get the product
    product_variations = []
    if request.method == "POST":
        for param in request.POST:
            key = param
            value = request.POST[key]
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                )
                product_variations.append(variation)
            except:
                pass

    try:
        cart = Cart.objects.get(
            cart_id=_cart_id(request=request)
        )  # get the cart using the cart_id presents in the session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request=request))
    cart.save()

    cart_items = CartItem.objects.filter(product=product, cart=cart)
    cart_item = None
    for single_cart_item in cart_items:
        # print(f"existing {list(single_cart_item.variations.all())}")
        # print(f"prodaction {product_variations}")
        if product_variations == list(single_cart_item.variations.all()):
            # increase the cart item quantity
            single_cart_item.quantity += 1
            single_cart_item.save()
            cart_item = single_cart_item
            break

    # if nothing existing found - create a new item
    if cart_item is None:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)

    if len(product_variations) > 0:
        cart_item.variations.add(*product_variations)

    cart_item.save()
    return redirect("cart")


def remove_cart(request, product_id, cart_item_id):
    cart_item = _get_cart_item(
        request=request, product_id=product_id, cart_item_id=cart_item_id
    )
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect("cart")


def remove_cart_item(request, product_id, cart_item_id):
    cart_item = _get_cart_item(
        request=request, product_id=product_id, cart_item_id=cart_item_id
    )
    cart_item.delete()
    return redirect("cart")


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request=request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        grand_total = 0
        tax = 0
    context = {
        "total": total,
        "quantity": quantity,
        "tax": tax,
        "grand_total": grand_total,
        "cart_items": cart_items,
    }
    return render(request=request, template_name="store/cart.html", context=context)
