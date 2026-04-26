import phonenumbers

from apps.user.models import CustomUser
from apps.user.api.v1.serializers import User_serializer
from core.base.crud import Core_crud


class User_services(Core_crud):
    model = CustomUser
    serializer = User_serializer

    @classmethod
    def get_user_by_number(cls, number):
        return cls.model.objects.filter(phone=number)

    @classmethod
    def number_format(cls, number):
        parsed = phonenumbers.parse(number, "RU")
        correct_number = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return correct_number

    @classmethod
    def plusofon_verify(cls, number: str):
        correct_number = cls.number_format(number)
        user = cls.get_user_by_number(correct_number)
        if not user.exists():
            return False
        user = user.first()
        user.is_active = True
        user.save()
        return True
