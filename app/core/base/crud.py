from abc import ABC, abstractmethod

from core.services.crud import Base_crud


class Core_crud(ABC):
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
        return Base_crud.update(cls.model, cls.serializer, data, parameters, context)

    @classmethod
    def get(cls, parameters: dict = {}, context: dict = None):
        return Base_crud.get(cls.model, cls.serializer, parameters, context)

    @classmethod
    def get_many(
        cls,
        parameters: dict = {},
        order: str = "id",
        custom_obj: dict = None,
        context: dict = None
    ):
        return Base_crud.get_many(cls.model, cls.serializer, parameters, order, custom_obj, context)

    @classmethod
    def create(cls, data: dict, context: dict = None):
        return Base_crud.create(cls.serializer, data, context)

    @classmethod
    def delete(cls, parameter: dict):
        return Base_crud.delete(cls.model, parameter)

    @classmethod
    def patch(cls, data: dict, parameters: dict, context: dict = None):
        return Base_crud.patch(cls.model, cls.serializer, data, parameters, context)
