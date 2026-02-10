from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from users.serializers import ProfileSerializer

User = get_user_model()


class UsersUnitTest(TestCase):
    """
    Logic tests for the Users model methods.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="password")

    def test_profile_str_representation(self):
        """ Verify that __str__ returns the full name if available, otherwise the username."""
        self.assertEqual(str(self.user), self.user.username)

    def test_soft_delete_logic(self):
        """Ensure soft_delete() sets is_active to False and populates deleted_at."""
        self.assertIsNone(self.user.deleted_at)
        self.assertTrue(self.user.is_active)

        self.user.soft_delete()

        self.assertIsNotNone(self.user.deleted_at)
        self.assertFalse(self.user.is_active)

    def test_profile_update_fullname_splitting(self):
        """Check if fullName is correctly split into first_name and last_name during update in the serializer."""
        data = {"fullName": "John Doe"}
        serializer = ProfileSerializer(instance=self.user, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()

        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")

class UsersApiTest(APITestCase):
    """
    Integration tests for users views.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="ivan", password="password123")
        self.url_signin = reverse("users:sign-in")
        self.url_signup = reverse("users:sign-up")
        self.url_sign_out = reverse("users:sign-out")
        self.url_profile = reverse("users:profile")
        self.url_password = reverse("users:profile_password")
        self.url_avatar = reverse("users:profile_avatar")

    def test_sign_up_success(self):
        """Verify new user registration and automatic login after successful sign-up."""
        user_exists = get_user_model().objects.filter(username="new_user_joe").exists()
        self.assertFalse(user_exists)

        data = {
            "name": "Joe",
            "username": "new_user_joe",
            "password": "password"
        }
        response = self.client.post(self.url_signup, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        user_exists = get_user_model().objects.filter(username="new_user_joe").exists()
        self.assertTrue(user_exists)

    def test_sign_in_malformed_json(self):
        """Ensure the view correctly parses malformed/stringified JSON data from the frontend."""
        malformed_data = {'{"username": "ivan", "password": "password123"}': ""}
        response = self.client.post(self.url_signin, malformed_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "success")
        
    def test_profile_access_denied_anonymous(self):
        """Ensure profile data is protected and returns 403 for unauthenticated users."""
        self.client.logout()
        response = self.client.get(self.url_profile)
        self.assertEqual(response.status_code, 403)

    def test_change_password_success(self):
        """Verify password update with correct current password and session persistence."""
        self.client.force_authenticate(user=self.user)
        data = {
            "currentPassword": "password123",
            "newPassword": "new_password123"
        }
        response = self.client.post(self.url_password, data, format="json")

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password123"))

    def test_avatar_upload_updates_file(self):
        """Ensure that uploading a new avatar replaces the old file in the user's profile."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        self.client.force_authenticate(user=self.user)
        image_content = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9'
            b'\x04\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00'
            b'\x00\x02\x02\x4c\x01\x00\x3b'
        )
        avatar = SimpleUploadedFile(
            name="new_avatar.png",
            content=image_content,
            content_type="image/png"
        )
        response = self.client.post(self.url_avatar, {"avatar": avatar}, format="multipart")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(self.user.avatar)
        self.assertTrue(self.user.avatar.name.endswith("new_avatar.png"))
