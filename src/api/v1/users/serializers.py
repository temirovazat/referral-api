from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model."""

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser')
