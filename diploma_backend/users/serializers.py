from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class AvatarSerializer(serializers.Serializer):
    src = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    def get_src(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return "/media/avatars/default-avatar.jpg"

    def get_alt(self, obj):
        return obj.get_full_name() if obj.get_full_name() else obj.username

class ProfileSerializer(serializers.ModelSerializer):
    fullName = serializers.CharField(source="get_full_name")
    avatar = AvatarSerializer(source="*", read_only=True)

    class Meta:
        model = User
        fields = ["id", "fullName", "email", "phone", "avatar"]

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def update(self, instance, data):
        if "get_full_name" in data:
            full_name = data.pop("get_full_name")

            if full_name:
                parts = full_name.split(" ", 1)
                instance.first_name = parts[0]
                instance.last_name = parts[1] if len(parts) > 1 else ''
        return super().update(instance, data)


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True, required=True)
    newPassword = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    def validate_currentPassword(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("The current password is entered incorrectly")
        return value

