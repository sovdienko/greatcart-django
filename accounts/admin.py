from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import Account, UserProfile


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


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html(
            '<img src="{}" width="30" style="border-redius:30%">'.format(
                object.profile_picture.url
            )
        )

    thumbnail.short_description = "Profile Picture"
    list_display = ("thumbnail", "user", "city", "state", "country")


# Register your models here.
admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
