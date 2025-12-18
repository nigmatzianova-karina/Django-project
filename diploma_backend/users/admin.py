from django.contrib import admin

from users.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["id", "get_full_name", "phone", "email", "is_active", "is_staff"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["first_name", "last_name", "phone", "email", "username"]
    ordering = ["is_active"]
