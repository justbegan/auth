from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
import logging

logger = logging.getLogger('django')


# класс APIView drf не добавляет контекст в сериализаторе, приходится в ручную получать

class Base_crud:
    @staticmethod
    def update(model: Model, serializer: ModelSerializer, data: dict, parameters: dict, context: dict = None):
        """
        Обновляет объект в базе
        """
        if context is None:
            context = {}
        instance = model.objects.get(**parameters)
        serializer = serializer(instance, data=data, context=context)

        if serializer.is_valid():
            serializer.save()
            return serializer.data
        raise serializers.ValidationError(serializer.errors)

    @staticmethod
    def get(model: Model, serializer: ModelSerializer, parameters: dict = {}, context: dict = None):
        """
        Получает 1 объект из базы
        """
        if context is None:
            context = {}
        try:
            obj = model.objects.get(**parameters)
            return serializer(obj, context=context).data
        except Exception as e:
            logger.exception(f"Ошибка получения данных в crud {e}")
            return {}

    @staticmethod
    def get_many(
        model: Model,
        serializer: ModelSerializer,
        parameters: dict = {},
        order: str = "id",
        custom_obj: dict = None,
        context: dict = None
    ):
        """
        Получает объекты из базы
        """
        if context is None:
            context = {}
        if custom_obj is None:
            obj = model.objects.filter(**parameters).order_by(order)
        else:
            obj = custom_obj
        return serializer(obj, many=True, context=context).data

    @staticmethod
    def create(serializer: ModelSerializer, data: dict, context: dict = None):
        """
        Создает объект в базе
        """
        if context is None:
            context = {}
        ser: ModelSerializer = serializer(data=data, context=context)
        if ser.is_valid():
            ser.save()
            return ser.data
        else:
            raise serializers.ValidationError(ser.errors)

    @staticmethod
    def delete(model: Model, parameter: dict):
        """
        Удаляет объект из базы
        """
        obj = model.objects.get(**parameter)
        obj.delete()
        return True

    @staticmethod
    def patch(model: Model, serializer: ModelSerializer, data: dict, parameters: dict, context: dict = None):
        """
        Обновляет поля объекта в базе
        """
        if context is None:
            context = {}
        instance = model.objects.get(**parameters)
        serializer = serializer(instance, data=data, partial=True, context=context)

        if serializer.is_valid():
            serializer.save()
            return serializer.data
        raise serializers.ValidationError(serializer.errors)
