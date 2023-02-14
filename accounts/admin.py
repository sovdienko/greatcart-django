from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account


class AccountAdmin(UserAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "last_login",
        "is_active",
        "date_joined",
    )
    list_display_links = ("email", "username")
    readonly_fields = ("last_login", "date_joined")
    ordering = ("-date_joined",)
    filter_horizontal = ()
    fieldsets = ()
    list_filter = ()


# Register your models here.
admin.site.register(Account, AccountAdmin)
