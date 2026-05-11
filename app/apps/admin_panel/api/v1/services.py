from core.base.crud import CoreCrud
from apps.admin_panel.api.v1.serializers import CategorySerializer, TariffSerializer
from apps.admin_panel.models import Category, Tariff


class CategoryServices(CoreCrud):
    model = Category
    serializer = CategorySerializer


class TariffServices(CoreCrud):
    model = Tariff
    serializer = TariffSerializer
