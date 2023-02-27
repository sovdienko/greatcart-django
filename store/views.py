from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from carts.models import CartItem
from carts.views import _cart_id
from category.models import Category
from orders.models import OrderProduct

from .forms import ReviewForm
from .models import Product, ProductGallery, ReviewRating


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

    if request.user.is_authenticated:
        try:
            order_product_exists = OrderProduct.objects.filter(
                user=request.user, product=product
            ).exists()
        except OrderProduct.DoesNotExist:
            order_product_exists = False
    else:
        order_product_exists = False

    # get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status_flag=True)

    # Get Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id=product.id)

    context = {
        "product": product,
        "in_cart": in_cart,
        "order_product_exists": order_product_exists,
        "reviews": reviews,
        "product_gallery": product_gallery,
    }

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


def submit_review(request, product_id):
    url = request.META.get("HTTP_REFERER")
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(
                user__id=request.user.id, product__id=product_id
            )
            # review willbe updated if exists
            form = ReviewForm(request.POST, instance=review)
            form.save()
            messages.success(request, "Thank you! Your review has been updated.")
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data["subject"]
                data.rating = form.cleaned_data["rating"]
                data.review = form.cleaned_data["review"]
                data.ip = request.META.get("REMOTE_ADDR")
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, "Thank you! Your review has been submitted.")
        return redirect(url)
