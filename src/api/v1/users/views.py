import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.serializers import (TokenRefreshSerializer,
                                                  TokenVerifySerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from users.models import AuthCode

from .serializers import (PhoneSendCodeSerializer, PhoneTokenSerializer,
                          UserDetailsSerializer, UserSerializer,
                          UserUpdateSerializer)

User = get_user_model()


@extend_schema(tags=['Users'])
class UserViewSet(ModelViewSet):
    """
    ViewSet for managing users.

    This ViewSet provides CRUD operations for the User model.
    """

    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('email', 'first_name', 'last_name',
                     'phone', 'invite_code', 'invited_by_code')
    filterset_fields = ('email', 'first_name', 'last_name',
                        'phone', 'invite_code', 'invited_by_code')
    http_method_names = ('get',)

    def get_serializer_class(self):
        """
        Return the serializer class based on the action.

        If the action is 'retrieve', return UserDetailsSerializer;
        otherwise, return UserSerializer.
        """
        if self.action == 'retrieve':
            return UserDetailsSerializer
        return UserSerializer

    @extend_schema(
        summary='Список пользователей',
    )
    def list(self, request, *args, **kwargs):
        """Get a list of all users."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary='Информация о пользователе',
    )
    def retrieve(self, request, *args, **kwargs):
        """Get information about a specific user."""
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['Users'])
class CurrentUserView(APIView):
    """
    API view for managing the current user.

    Provides endpoints for retrieving and updating the current user's information.
    """

    @extend_schema(
        summary='Текущий пользователь',
        description='Возвращает текущего пользователя',
        responses={200: UserDetailsSerializer}
    )
    def get(self, request):
        """
        Retrieve details of the current user.

        Returns:
            Response: Serialized data of the current user.
        """
        serializer = UserDetailsSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary='Текущий пользователь',
        description='Изменение текущего пользователя',
        request=UserUpdateSerializer,
        responses={200: UserDetailsSerializer}
    )
    def patch(self, request):
        """
        Update details of the current user.

        Args:
            request: Request object containing the updated user data.

        Returns:
            Response: Serialized data of the updated current user.
        """
        user = request.user
        serializer = UserUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(tags=['Auth'])
class PhoneSendCodeView(APIView):
    """View to send authentication code to the users phone."""

    permission_classes = (AllowAny,)
    serializer_class = PhoneSendCodeSerializer

    @extend_schema(
        summary='Прислать код на номер телефона',
        description=(
            'Присваивает указанному номеру телефона 4-х значный код и возвращает его в ответе.'
        ),
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='code',
                fields={'code': serializers.IntegerField()}
            )
        }
    )
    def post(self, request):
        """
        Handle POST requests for sending authentication code.

        Returns:
        - `code`: Authentication code sent to the user's phone.

        Raises:
        - `400 Bad Request` if the serializer is not valid.
        """
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data.get('phone')
        auth_code = random.randint(1000, 9999)
        hashed_code = make_password(str(auth_code), salt=None)

        AuthCode.objects.update_or_create(
            phone=phone,
            defaults={
                'code': hashed_code,
                'created': timezone.now()
            }
        )

        return Response({'code': auth_code}, status=status.HTTP_200_OK)


@extend_schema(tags=['Auth'])
class PhoneTokenView(APIView):
    """View to exchange authentication code for an access token."""

    permission_classes = (AllowAny,)
    serializer_class = PhoneTokenSerializer

    @extend_schema(
        summary='Получение токенов по номеру телефона и коду',
    )
    def post(self, request):
        """
        Handle POST requests for exchanging authentication code for an access token.

        Returns:
        - `access`: Access token.
        - `refresh`: Refresh token.

        Raises:
        - `400 Bad Request` if the serializer is not valid.
        - `403 Forbidden` for incorrect code or expired code.
        """
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        phone = serializer.validated_data.get('phone')
        code = serializer.validated_data.get('code')
        invited_by_code = serializer.validated_data.get('invited_by_code')

        auth_code = AuthCode.objects.filter(phone=phone).first()

        if not auth_code or not check_password(code, auth_code.code):
            return Response(
                {'code': 'Неверный код.'},
                status=status.HTTP_403_FORBIDDEN
            )
        difference = timezone.now() - auth_code.created
        time_expires = int(settings.AUTH_CODE_EXPIRES_MINUTES)
        if difference > timezone.timedelta(minutes=time_expires):
            return Response(
                {'code': 'Время действия кода истекло.'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_data = {'invited_by_code': None}

        if invited_by_code:
            user = User.objects.filter(invite_code=invited_by_code)
            if not user.exists():
                return Response(
                    {'invited_by_code': 'Неверный реферальный код.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            user_data['invited_by_code'] = invited_by_code

        user, _ = User.objects.update_or_create(
            phone=phone,
            defaults=user_data
        )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        auth_code.delete()
        return Response(
            {'access': access_token, 'refresh': str(refresh)},
            status=status.HTTP_200_OK
        )


@extend_schema(tags=['Auth'])
class TokenRefreshView(TokenRefreshView):
    """
    Custom view for refreshing an access token.

    Extends the default TokenRefreshView to customize behavior.
    """

    serializer_class = TokenRefreshSerializer

    @extend_schema(
        summary='Рефреш токена',
    )
    def post(self, request, *args, **kwargs):
        """
        Refresh an access token.

        Perform the token refresh and return the new access token.

        Args:
            request: The HTTP request.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            The HTTP response with the new access token.
        """
        return super().post(request, *args, **kwargs)


@extend_schema(tags=['Auth'])
class TokenVerifyView(TokenVerifyView):
    """
    Custom view for verifying an access token.

    Extends the default TokenVerifyView to customize behavior.
    """

    serializer_class = TokenVerifySerializer

    @extend_schema(
        summary='Проверка токена',
    )
    def post(self, request, *args, **kwargs):
        """
        Verify an access token.

        Perform the token verification and return the verification result.

        Args:
            request: The HTTP request.
            args: Additional positional arguments.
            kwargs: Additional keyword arguments.

        Returns:
            The HTTP response with the verification result.
        """
        return super().post(request, *args, **kwargs)
