from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Custom manager for the User model.

    Provides helper methods for creating regular and superuser instances of the User model.
    """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and return a regular user with an email and password.

        :param email: The user's email address.
        :param password: The user's password.
        :param extra_fields: Additional fields to include in the user creation.
        :return: A new regular user instance.
        """
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user.

        :param email: The user's email address.
        :param password: The user's password.
        :param extra_fields: Additional fields to include in the user creation.
        :return: A new regular user instance.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser.

        :param email: The superuser's email address.
        :param password: The superuser's password.
        :param extra_fields: Additional fields to include in the superuser creation.
        :return: A new superuser instance.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self._create_user(email, password, **extra_fields)
