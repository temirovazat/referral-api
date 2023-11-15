from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserChangeForm(UserChangeForm):
    """Form for updating user information."""

    class Meta(UserChangeForm.Meta):
        model = User
        fields = '__all__'


class CustomUserCreationForm(UserCreationForm):
    """Form for creating a new user."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs['autocomplete'] = 'off'
        self.fields['password2'].widget.attrs['autocomplete'] = 'off'

    def clean_password2(self):
        """
        Clean the password confirmation.

        Check that the password confirmation matches the entered password.
        """
        password1 = self.cleaned_data.get('password1')
        password2 = super(UserCreationForm, self).clean_password2()
        if bool(password1) ^ bool(password2):
            raise forms.ValidationError('Fill out both fields')
        return password2


class CustomUserAdmin(BaseUserAdmin):
    """Custom admin configuration for the User model."""

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('email', 'phone', 'invite_code', 'date_joined')
    ordering = ('date_joined',)
    fieldsets = (
        (
            ('Basic Information'),
            {'fields': ('email', 'phone', 'invite_code', 'invited_by_code',
                        'first_name', 'last_name', 'password')}
        ),
        (
            ('Roles and Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (
            ('Dates'),
            {'fields': ('last_login', 'date_joined')}
        ),
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': (
        'phone', 'invited_by_code', 'email', 'first_name', 'last_name',
        'password1', 'password2'
    ), }), )
    readonly_fields = ('invite_code',)


admin.site.register(User, CustomUserAdmin)
