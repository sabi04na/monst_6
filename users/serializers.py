from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserBaseSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=150)
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        try:
            CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return email
        raise ValidationError("User уже существует!")


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        if user.birthdate:
            token['birthdate'] = str(user.birthdate)
        else:
            token['birthdate'] = None
        return token