from django.http import HttpRequest
from django.shortcuts import render

from store.models import Product


def home(request: HttpRequest):
    products = Product.objects.all().filter(is_available=True).order_by("created_date")

    context = {
        "products": products,
    }
    return render(request=request, template_name="home.html", context=context)
