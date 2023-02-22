from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator

# Verification Email
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from requests import utils

from carts.models import Cart, CartItem
from carts.views import _cart_id

from .forms import RegistrationForm
from .models import Account


# Create your views here.
def _sent_email(request, mail_subject, user, refirect_html, to_email):
    current_site = get_current_site(request)
    message = render_to_string(
        f"accounts/{refirect_html}.html",
        {
            "user": user,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": default_token_generator.make_token(user),
        },
    )
    send_emal = EmailMessage(mail_subject, message, to=[to_email])
    send_emal.send()


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()

            # User Activation
            _sent_email(
                request=request,
                mail_subject="Please activate your account",
                user=user,
                refirect_html="account_verification_email",
                to_email=email,
            )

            return redirect("/accounts/login/?command=verification&email=" + email)
    else:
        # GET request and render the Regisytration form
        form = RegistrationForm()

    context = {"form": form}
    return render(
        request=request, template_name="accounts/register.html", context=context
    )


def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request=request))
                cart_items = CartItem.objects.filter(cart=cart)
                # to assign and group together items in the Cart and items already assigned to the User
                for cart_item in cart_items:
                    # getting Items assigned to the user
                    cart_item_var = list(cart_item.variations.all())
                    user_cart_items = CartItem.objects.filter(user=user)
                    for user_cart_item in user_cart_items:
                        user_cart_item_var = list(user_cart_item.variations.all())
                        is_added = False
                        if (
                            cart_item.product == user_cart_item.product
                            and cart_item_var == user_cart_item_var
                        ):
                            # increase the cart item quantity
                            user_cart_item.quantity += cart_item.quantity
                            user_cart_item.save()
                            is_added = True
                            break

                        if not is_added:
                            cart_item.user = user
                            cart_item.save()

            except Exception as exp:
                print(type(exp))

            auth.login(request, user)
            messages.success(request, "You are now login.")
            url = request.META.get("HTTP_REFERER")
            print(f"{url=}")
            try:
                query = utils.urlparse(url).query
                # next=carts/checkout/
                params = dict(param.split("=") for param in query.split("&"))
                if "next" in params:
                    next_page = params["next"]
                    return redirect(next_page)
                else:
                    return redirect("dashboard")
            except:
                return redirect("dashboard")
        else:
            messages.error(request=request, message="Invalid login credentials.")
            return redirect("login")
    return render(request=request, template_name="accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request=request)
    messages.success(request=request, message="You are logged out.")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request=request, message="Congadulations! You account is activated."
        )
        return redirect("login")
    else:
        messages.error(request=request, message="Invalid activation link")
        return redirect("register")


@login_required(login_url="login")
def dashboard(request):
    return render(request=request, template_name="accounts/dashboard.html")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)

            # User Reset Password email
            _sent_email(
                request=request,
                mail_subject="Please reset your Password",
                user=user,
                refirect_html="reset_password_email",
                to_email=email,
            )

            messages.success(
                request=request,
                message="Password reset email has been sent to your email address.",
            )
            return redirect("login")
        else:
            messages.error(request=request, message="Account does not exists!")
            return redirect("forgotPassword")
    else:
        # Get request
        return render(request=request, template_name="accounts/forgotPassword.html")


def reset_password_validate(request, uidb64, token):
    uid = ""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request=request, message="Please reset your passowrd.")
        return redirect("resetPassword")
    else:
        messages.error(request=request, message="This link has been expired!")
        return redirect("login")


def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirmed_password = request.POST["confirmed_password"]
        if confirmed_password == password:
            uid = request.session.get("uid")
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request=request, message="Password does not match")
            return redirect("resetPassword")
    else:
        return render(request=request, template_name="accounts/resetPassword.html")
