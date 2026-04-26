from rest_framework import serializers

from apps.user.models import CustomUser


class User_serializer(serializers.ModelSerializer):
    profiles = serializers.ListField(read_only=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'profiles', 'email',
                  'first_name', 'patronymic', 'last_name', 'phone']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
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


class Plusofon_serializer(serializers.Serializer):
    from_ = serializers.CharField(source="from")
