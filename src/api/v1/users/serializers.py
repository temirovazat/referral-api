from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class InvitedUserSerializer(serializers.ModelSerializer):
    """Serializer for the invited user model."""

    class Meta:
        model = User
        fields = ('id', 'phone')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user model."""

    class Meta:
        model = User
        exclude = ('password', 'groups', 'user_permissions', 'is_superuser')


class UserDetailsSerializer(UserSerializer):
    """Serializer for the user model with details."""

    invited = serializers.SerializerMethodField()

    @extend_schema_field(InvitedUserSerializer(many=True))
    def get_invited(self, obj):
        """
        Get the list of invited users.

        This method retrieves the list of users invited by the current user.
        """
        invited_users = User.objects.filter(
            invited_by_code__iexact=obj.invite_code
        )
        invited_serializer = InvitedUserSerializer(invited_users, many=True)
        return invited_serializer.data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for the user model for updating."""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'invited_by_code', 'email')

    def validate_invited_by_code(self, value):
        """
        Validate the invited by code.

        This method validates the invited by code field to ensure it is not the user's
        own code and that it corresponds to an existing user.
        """
        user = self.instance

        if value.lower() == user.invite_code.lower():
            raise serializers.ValidationError('Cannot specify your own code.')

        try:
            User.objects.get(invite_code__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with this code does not exist.'
            )

        return value

    def to_representation(self, instance):
        """
        Convert the instance to representation.

        This method converts the user instance to its representation using the
        UserDetailsSerializer.
        """
        return UserDetailsSerializer(instance, context=self.context).data


class PhoneSendCodeSerializer(serializers.Serializer):
    """Serializer for sending phone code."""

    phone = PhoneNumberField()

    class Meta:
        fields = ('phone',)


class PhoneTokenSerializer(serializers.Serializer):
    """Serializer for validating phone code."""

    phone = PhoneNumberField()
    code = serializers.IntegerField()
    invited_by_code = serializers.CharField(required=False)
