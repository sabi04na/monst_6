from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("EMAIL is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        phone_number = extra_fields.get("phone_number")
        if not phone_number:
            raise ValueError("Superuser must have a phone_number.")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be is_staff True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be is_superuser True")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must be is_active True")

        return self.create_user(email, password, **extra_fields)
