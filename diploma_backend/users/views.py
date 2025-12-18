from django.contrib.auth import get_user_model, update_session_auth_hash
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

@api_view(["GET"])
def profile_history_orders_view(request):
    pass
