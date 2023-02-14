from django.shortcuts import get_object_or_404, render

from category.models import Category

from .models import Product


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is None:
        products = Product.objects.all().filter(is_available=True)
    else:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=categories, is_available=True)

    product_count = products.count()
    context = {"products": products, "product_count": product_count}
    return render(request=request, template_name="store/store.html", context=context)


def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as exp:
        raise exp
    context = {"product": product}

    return render(
        request=request, template_name="store/product_detail.html", context=context
    )
