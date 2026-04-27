from rest_framework import serializers

from apps.user.models import CustomUser
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    profiles = serializers.ListField(read_only=True)
    phone = serializers.CharField(
        validators=[UniqueValidator(queryset=CustomUser.objects.all(), message="Телефон уже используется")],
        required=True
    )
    is_active = serializers.BooleanField(read_only=True)
    full_name = serializers.CharField(read_only=True, source='get_full_name_v2')

    class Meta:
        model = CustomUser
        fields = ['id', 'password', 'profiles', 'email', 'is_active',
                  'first_name', 'patronymic', 'last_name', 'phone', 'full_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        user.username = validated_data['email']
        user.is_active = False
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PlusofonSerializer(serializers.Serializer):
    from_ = serializers.CharField(source="from")
