from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class AvatarSerializer(serializers.Serializer):
    """
    Serializes user avatar details.
    Provides a source URL and alternative text based on user's name.
    """
    src = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    def get_src(self, obj):
        """Returns the avatar URL or path to the default placeholder."""
        if obj.avatar:
            return obj.avatar.url
        return "/media/avatars/default-avatar.jpg"

    def get_alt(self, obj):
        """Returns the user's full name or nickname for the alt attribute."""
        return obj.get_full_name() if obj.get_full_name() else obj.username

class ProfileSerializer(serializers.ModelSerializer):
    """
    Handles user profile data. 
    Supports updating full name by splitting it into first and last name fields.
    Includes unique email validation excluding the current user.
    """
    fullName = serializers.CharField(source="get_full_name", required=False)
    avatar = AvatarSerializer(source="*", read_only=True)

    class Meta:
        model = User
        fields = ["id", "fullName", "email", "phone", "avatar"]

    def validate_email(self, value):
        """Checks if the email is already taken by another user."""
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def update(self, instance, data):
        """
        Custom update logic to handle the 'fullName' virtual field 
        and distribute it to first_name and last_name.
        """
        if "get_full_name" in data:
            full_name = data.pop("get_full_name").strip()

            if full_name:
                parts = full_name.split(" ", 1)
                instance.first_name = parts[0]
                instance.last_name = parts[1] if len(parts) > 1 else ''
            else:
                instance.first_name = ""
                instance.last_name = ""
        return super().update(instance, data)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Validates and processes password changes.
    Verifies current password and applies Django's standard password strength rules.
    """
    currentPassword = serializers.CharField(write_only=True, required=True)
    newPassword = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def validate_currentPassword(self, value):
        """Checking the compliance of the current user password."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("The current password is entered incorrectly")
        return value
