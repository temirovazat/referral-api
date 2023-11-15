import random
import string

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for the application."""

    phone = PhoneNumberField(
        verbose_name=_('phone'),
        max_length=12,
        unique=True,
        blank=True,
        null=True
    )
    invite_code = models.CharField(
        verbose_name=_('invite code'),
        max_length=6,
        default=None,
        unique=True
    )
    invited_by_code = models.CharField(
        verbose_name=_('invited by code'),
        max_length=6,
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name=_('email'),
        unique=True,
        max_length=254,
        blank=True,
        null=True
    )
    first_name = models.CharField(
        verbose_name=_('first name'),
        max_length=32,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name=_('last name'),
        max_length=32,
        blank=True,
        null=True
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        """Return the invite code of the user as a string.

        Returns:
            str: The invite code of the user.
        """
        return str(self.invite_code)

    def save(self, *args, **kwargs):
        """Save the user instance.

        If the instance is being added, generate a unique invite code.

        Args:
            *args: Additional arguments.
            **kwargs: Additional keyword arguments.

        """
        if self._state.adding:
            self.invite_code = self.generate_invite_code()
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def clean(self):
        """Clean method to validate data before saving.

        Raises:
            ValidationError: If invited_by_code is the same as the invite_code.
            ValidationError: If the user with invited_by_code does not exist.

        """
        if self.invited_by_code:
            if self.invited_by_code == self.invite_code:
                raise ValidationError(
                    {'invited_by_code': 'Cannot specify your own code.'}
                )

            try:
                User.objects.get(invite_code__iexact=self.invited_by_code)
            except User.DoesNotExist:
                raise ValidationError(
                    {'invited_by_code': 'User with this code does not exist.'}
                )
        super().clean()

    def generate_invite_code(self):
        """Generate a unique invite code.

        Returns:
            str: The generated invite code.

        """
        while True:
            code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=6
            ))
            if not User.objects.filter(invite_code__iexact=code).exists():
                return code
