from django.contrib.auth.models import AbstractUser
from django.db import models


class Profile(AbstractUser):
    """
    Custom User model representing a site member.
    Extends Django's AbstractUser with additional fields for contact information,
    personalization, and soft-delete functionality.
    """
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Номер телефона")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Время удаления")

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Returns the string representation of the user (Username or Full Name)."""
        return self.get_full_name() or self.username

    def soft_delete(self):
        """Marks the profile as deleted without removing it from the database."""
        import django.utils.timezone
        self.deleted_at = django.utils.timezone.now()
        self.is_active = False
        self.save()
