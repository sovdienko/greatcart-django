from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category

from .models import Product


# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug is None:
        products = Product.objects.all().filter(is_available=True).order_by("id")
    else:
        categories = get_object_or_404(Category, slug=category_slug)
        products = (
            Product.objects.all()
            .filter(category=categories, is_available=True)
            .order_by("id")
        )

    paginator = Paginator(products, 2)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)

    product_count = products.count()
    context = {"products": paged_products, "product_count": product_count}
    return render(request=request, template_name="store/store.html", context=context)


def product_detail(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request=request), product=product
        ).exists()
    except Exception as exp:
        raise exp
    context = {"product": product, "in_cart": in_cart}

    return render(
        request=request, template_name="store/product_detail.html", context=context
    )


def search(request):
    products = {}
    product_count = 0
    if "keyword" in request.GET:
        keyword = request.GET["keyword"]
        if keyword:
            products = Product.objects.filter(
                Q(product_description__icontains=keyword)
                | Q(product_name__icontains=keyword)
            ).order_by("-created_date")
            product_count = products.count()

    context = {
        "products": products,
        "product_count": product_count,
    }
    return render(request=request, template_name="store/store.html", context=context)
