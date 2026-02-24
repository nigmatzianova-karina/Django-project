from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


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


@receiver(pre_save, sender=Profile)
def delete_old_avatar_on_change(sender, instance, **kwargs):
    """Deletes the old avatar file before saving the new one, unless this is the default."""
    if not instance.pk:
        return False

    try:
        old_avatar = Profile.objects.get(pk=instance.pk).avatar
    except Profile.DoesNotExist:
        return False

    new_avatar = instance.avatar

    if old_avatar and old_avatar != new_avatar:
        if 'default-avatar.jpg' not in old_avatar.name:
            if old_avatar.storage.exists(old_avatar.name):
                old_avatar.storage.delete(old_avatar.name)
