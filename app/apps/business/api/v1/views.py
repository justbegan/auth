from django.db.models import Avg, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.business.api.v1.serializers import (
    BusinessAnalyticsDailySerializer,
    BusinessSerializer,
    OrderSerializer,
    OrderStatusSerializer,
    ProductImportJobSerializer,
    ProductSerializer,
)
from apps.business.filters import BusinessAnalyticsDailyFilter, OrderFilter, ProductFilter
from apps.business.models import Business, BusinessAnalyticsDaily, Order, Product, ProductImportJob
from apps.city.models import ChatConversation
from core.permissions import IsBusinessAccount


class DashboardQuerysetMixin:
    permission_classes = [IsBusinessAccount]
    filter_backends = [DjangoFilterBackend]

    def _business_id_from_request(self):
        return self.request.query_params.get('business_id')

    def get_business(self):
        if getattr(self, 'swagger_fake_view', False) or not self.request.user.is_authenticated:
            return None
        business_id = self._business_id_from_request()
        if getattr(self.request.user, 'account_type', None) == 'admin' or self.request.user.is_staff:
            if not business_id:
                return None
            return Business.objects.filter(id=business_id).first()
        return Business.objects.filter(owner=self.request.user).first()


@extend_schema(tags=['Business Dashboard: Overview'])
class DashboardOverview(APIView):
    permission_classes = [IsBusinessAccount]
    serializer_class = BusinessSerializer

    def get(self, request):
        business_id = request.query_params.get('business_id')
        if request.user.is_staff or getattr(request.user, 'account_type', None) == 'admin':
            business = Business.objects.filter(id=business_id).first() if business_id else None
        else:
            business = Business.objects.filter(owner=request.user).first()
        if not business:
            return Response({'detail': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)

        orders = business.orders.all()
        analytics = business.analytics_daily.all()
        payload = {
            'business': BusinessSerializer(business, context={'request': request}).data,
            'views': analytics.aggregate(total=Sum('views'))['total'] or 0,
            'orders_count': orders.count(),
            'revenue_total': orders.aggregate(total=Sum('total'))['total'] or 0,
            'rating': business.rating,
            'avg_check': orders.aggregate(avg=Avg('total'))['avg'] or 0,
            'latest_orders': OrderSerializer(orders.order_by('-created_at')[:5], many=True).data,
        }
        return Response(payload)


@extend_schema(tags=['Business Dashboard: Profile'])
class DashboardProfile(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessSerializer
    permission_classes = [IsBusinessAccount]

    def get_object(self):
        business_id = self.request.query_params.get('business_id')
        if self.request.user.is_staff or getattr(self.request.user, 'account_type', None) == 'admin':
            business = Business.objects.filter(id=business_id).first() if business_id else None
        else:
            business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            from django.http import Http404
            raise Http404
        return business


@extend_schema(tags=['Business Dashboard: Products'])
class ProductViewSet(DashboardQuerysetMixin, viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        business = self.get_business()
        if not business:
            return Product.objects.none()
        return Product.objects.filter(business=business).order_by('sort_order', 'name')

    @action(detail=False, methods=['post'], serializer_class=ProductImportJobSerializer)
    def import_file(self, request):
        business = self.get_business()
        if not business:
            return Response({'detail': 'Business not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImportJobSerializer(data={**request.data, 'business': business.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(status=ProductImportJob.Status.QUEUED)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        business = self.get_business()
        serializer.save(business=business)


@extend_schema(tags=['Business Dashboard: Orders'])
class DashboardOrderViewSet(DashboardQuerysetMixin, mixins.ListModelMixin,
                            mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = OrderSerializer
    filterset_class = OrderFilter

    def get_queryset(self):
        business = self.get_business()
        if not business:
            return Order.objects.none()
        return Order.objects.filter(business=business).order_by('-created_at')

    @action(detail=True, methods=['patch'], serializer_class=OrderStatusSerializer)
    def status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order.status = serializer.validated_data['status']
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['get'])
    def chat(self, request, pk=None):
        order = self.get_object()
        conversation = ChatConversation.objects.filter(order=order).first()
        return Response({'conversation_id': conversation.id if conversation else None})


@extend_schema(tags=['Business Dashboard: Analytics'])
class DashboardAnalyticsViewSet(DashboardQuerysetMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = BusinessAnalyticsDailySerializer
    filterset_class = BusinessAnalyticsDailyFilter

    def get_queryset(self):
        business = self.get_business()
        if not business:
            return BusinessAnalyticsDaily.objects.none()
        return BusinessAnalyticsDaily.objects.filter(business=business).order_by('-day')
