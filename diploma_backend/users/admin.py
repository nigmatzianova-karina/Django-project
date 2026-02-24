from django.contrib import admin
from django.utils.html import format_html

from users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Administrative interface for User Profiles.
    Extends standard User management with custom fields like phone and avatar.
    """
    list_display = ["id", "avatar_preview", "username", "full_name_display", "phone", "email", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff", "date_joined"]
    search_fields = ["first_name", "last_name", "phone", "email", "username"]
    ordering = ["-date_joined"]
    list_editable = ["is_active"]

    def full_name_display(self, obj):
        """Returns the user's full name or username if name is not set."""
        return obj.get_full_name() or obj.username

    full_name_display.short_description = "Full Name"
    full_name_display.admin_order_field = "first_name"

    def avatar_preview(self, obj):
        """Displays a small thumbnail of the user's avatar in the list view."""
        if obj.avatar:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%;" />',
                               obj.avatar.url)
        return format_html('<div style="width: 30px; height: 30px; background: #ddd; border-radius: 50%;"></div>')

    avatar_preview.short_description = "Pic"
