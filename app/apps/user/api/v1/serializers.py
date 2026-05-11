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
                  'first_name', 'last_name', 'phone', 'full_name',
                  'account_type', 'status', 'last_login', 'created_at',
                  'updated_at']
        read_only_fields = ['id', 'last_login', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        request = self.context.get('request')
        password = validated_data.pop('password', None)
        requested_account_type = validated_data.pop('account_type', CustomUser.AccountType.USER)
        can_manage_roles = bool(
            request
            and request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, 'account_type', None) == CustomUser.AccountType.ADMIN)
        )
        account_type = requested_account_type if can_manage_roles else CustomUser.AccountType.USER
        user = CustomUser(**validated_data)
        user.account_type = account_type
        user.username = validated_data['email']
        user.is_active = False
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')
        password = validated_data.pop('password', None)
        account_type = validated_data.pop('account_type', None)
        if account_type is not None:
            can_manage_roles = bool(
                request
                and request.user
                and request.user.is_authenticated
                and (request.user.is_staff or getattr(request.user, 'account_type', None) == CustomUser.AccountType.ADMIN)
            )
            if can_manage_roles:
                instance.account_type = account_type
        if password:
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PlusofonSerializer(serializers.Serializer):
    from_ = serializers.CharField(source="from")
