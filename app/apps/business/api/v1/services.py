from core.base.crud import CoreCrud
from apps.business.api.v1.serializers import BusinessSerializer, ProductSerializer
from apps.business.models import Business, Product


class BusinessServices(CoreCrud):
    model = Business
    serializer = BusinessSerializer


class ProductServices(CoreCrud):
    model = Product
    serializer = ProductSerializer
