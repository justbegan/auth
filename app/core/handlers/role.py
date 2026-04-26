from functools import wraps
import logging
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import Response, Request
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from apps.user.models import Role_handler, Method
from core.helpers.role import get_role_by_tech_name

logger = logging.getLogger('django')


ROLES = (
    (1, "Администратор"),
    (2, "Модератор"),
    (3, "Оператор"),
    (4, "Пользователь"),
)


def role_required():
    def decorator(func):
        @wraps(func)
        def wrapper(self, request: Request, *args, **kwargs):
            method = Method.objects.get(title=str(request.method).lower())
            if request.method == 'POST':
                error_text = "У вас нет прав для создания записи."
            else:
                error_text = "У вас нет прав для изменения записи."
            user_role = request.user.role
            used_model_content_type = ContentType.objects.get_for_model(self.model_used)
            if user_role in [get_role_by_tech_name('admin'), get_role_by_tech_name('moder')]:
                return func(self, request, *args, **kwargs)
            try:
                method_roles = Role_handler.objects.filter(
                    agency=request.user.agency,
                    model=used_model_content_type,
                    roles=user_role,
                    methods=method
                ).last()
                if not method_roles:
                    return Response(
                        {"message": error_text},
                        status=status.HTTP_403_FORBIDDEN
                    )
                if not method_roles.roles.filter(id=user_role.id):
                    return Response(
                        {"message": error_text},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except ObjectDoesNotExist as e:
                logger.exception(f"Не могу найти роль метода {e}")
                return Response(
                    {"message": error_text},
                    status=status.HTTP_403_FORBIDDEN
                )

            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator
