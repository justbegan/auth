from apps.user.models import CustomUser
from apps.user.api.v1.serializers import User_serializer
from core.base.crud import Core_crud


class User_services(Core_crud):
    model = CustomUser
    serializer = User_serializer
