from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['groups'] = cls._get_groups(user)
        token['full_name'] = cls._get_full_name(user)
        token['organization'] = cls._get_organization(user)

        return token

    @staticmethod
    def _get_groups(user):
        return list(user.groups.values_list('name', flat=True))

    @staticmethod
    def _get_full_name(user):
        if hasattr(user, 'get_full_name_v2'):
            return user.get_full_name_v2()
        return None

    @staticmethod
    def _get_organization(user):
        if hasattr(user, 'get_org'):
            return user.get_org()
        return None


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
