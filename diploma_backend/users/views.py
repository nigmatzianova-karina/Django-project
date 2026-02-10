import json
from django.contrib.auth import get_user_model, update_session_auth_hash, authenticate, login, logout
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import ProfileSerializer, ChangePasswordSerializer

User = get_user_model()


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Manages the user's personal profile information.
    GET: Returns the current user's profile details.
    POST: Updates profile fields (e.g., fullName, email, phone) using partial data.
    """
    if request.method == "GET":
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    return Response(status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profile_avatar_view(request):
    """
    Updates the user's profile picture.
    Deletes the old avatar file from storage before saving the new one.
    Expects a multipart/form-data request with an 'avatar' file.
    """
    if 'avatar' not in request.FILES:
        return Response(
            {"error": "No avatar file provided"},
            status=400
        )

    user = request.user
    if user.avatar:
        user.avatar.delete(save=False)

    user.avatar = request.FILES["avatar"]
    user.save()
    return Response(status=200)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profile_password_view(request):
    """
    Changes the authenticated user's password.
    Verifies the current password and validates the complexity of the new one.
    Updates the session to prevent automatic logout after password change.
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        user = request.user
        user.set_password(serializer.validated_data["newPassword"])
        user.save()
        update_session_auth_hash(request, user)
        return Response(status=200)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
def sign_in_view(request):
    """
    Authenticates an existing user via username and password.
    Includes a fallback parser for malformed JSON strings from the frontend.
    Starts a persistent web session upon successful authentication.
    """
    data = request.data

    if not request.query_params and len(data) == 1 and "" in data.values():
        try:
            raw_json = list(data.keys())[0]
            data = json.loads(raw_json)
        except Exception as e:
            print(f"error: {e}")
            pass

    username = data.get("username")
    password = data.get("password")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        return Response({"status": "success"}, status=200)

    return Response({"error": "Invalid credentials"}, status=401)


@api_view(["POST"])
def sign_up_view(request):
    """
    Creates a new user profile with the provided name, username, and password.
    Automatically logs in the user after successful registration.
    Handles malformed frontend JSON strings.
    """
    data = request.data

    if not request.query_params and len(data) == 1 and "" in data.values():
        try:
            if data:
                raw_json = list(data.keys())[0]
                data = json.loads(raw_json)
        except Exception as e:
            print(f"error: {e}")
            pass

    name = data.get("name")
    username = data.get("username")
    password = data.get("password")

    if User.objects.filter(username=username).exists():
        return Response({"error": "User already exists"}, 500)

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=name
        )
        login(request, user)
        return Response({"status": "success"}, 200)
    except Exception as e:
        return Response({"error": str(e)}, 500)


@api_view(["POST"])
def sign_out_view(request):
    """
    Ends the current user session and clears authentication cookies.
    """
    logout(request)
    return Response({"status": "success"}, 200)
