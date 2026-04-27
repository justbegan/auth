from abc import ABC, abstractmethod

from core.services.crud import BaseCrud


class CoreCrud(ABC):
    @property
    @abstractmethod
    def model(cls):
        ...

    @property
    @abstractmethod
    def serializer(cls):
        ...

    @classmethod
    def update(cls, data: dict, parameters: dict, context: dict = None):
        return BaseCrud.update(cls.model, cls.serializer, data, parameters, context)

    @classmethod
    def get(cls, parameters: dict = {}, context: dict = None):
        return BaseCrud.get(cls.model, cls.serializer, parameters, context)

    @classmethod
    def get_many(
        cls,
        parameters: dict = {},
        order: str = "id",
        custom_obj: dict = None,
        context: dict = None
    ):
        return BaseCrud.get_many(cls.model, cls.serializer, parameters, order, custom_obj, context)

    @classmethod
    def create(cls, data: dict, context: dict = None):
        return BaseCrud.create(cls.serializer, data, context)

    @classmethod
    def delete(cls, parameter: dict):
        return BaseCrud.delete(cls.model, parameter)

    @classmethod
    def patch(cls, data: dict, parameters: dict, context: dict = None):
        return BaseCrud.patch(cls.model, cls.serializer, data, parameters, context)
