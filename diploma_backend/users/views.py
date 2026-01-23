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
    if request.method == "GET":
        serializer = ProfileSerializer(request.user)

        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProfileSerializer(request.user, data=request.data, partial=True, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    return Response(status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def profile_avatar_view(request):
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
def profile_password_view(request):
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )

    if serializer.is_valid():
        user = request.user
        user.set_passsword(serializer.validated_data("newPassword"))
        user.save()
        update_session_auth_hash(request, user)
    return Response(status=200)


@api_view(["POST"])
def sign_in_view(request):
    print("sign in")
    data = request.data

    if not request.query_params and len(data) == 1 and "" in data.values():
        try:
            raw_json = list(data.keys())[0]
            data = json.loads(raw_json)
        except Exception as e:
            print(f"error: {e}")
            pass

    username = data.get("username")
    print(username)

    password = data.get("password")
    print(password)

    user = authenticate(request, username=username, password=password)
    print(user)

    if user is not None:
        login(request, user)
        return Response({"status": "success"}, status=200)

    return Response({"error": "Invalid credentials"}, status=500)


@api_view(["POST"])
def sign_up_view(request):
    data = request.data

    if not request.query_params and len(data) == 1 and "" in data.values():
        try:
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
    logout(request)
    return Response({"status": "success"}, 200)
