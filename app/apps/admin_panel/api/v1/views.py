from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.admin_panel.api.v1.serializers import (
    AdCampaignSerializer,
    AdminStatsDailySerializer,
    CategorySerializer,
    RejectSerializer,
    ReviewReportSerializer,
    TariffSerializer,
)
from apps.admin_panel.filters import (
    AdCampaignFilter,
    AdminBusinessFilter,
    AdminReviewFilter,
    AdminStatsDailyFilter,
    AdminUserFilter,
    CategoryFilter,
    ReviewReportFilter,
    TariffFilter,
)
from apps.admin_panel.models import AdCampaign, AdminStatsDaily, Category, ModerationCase, ReviewReport, Tariff
from apps.business.api.v1.serializers import BusinessSerializer
from apps.business.models import Business
from apps.city.api.v1.serializers import ReviewSerializer
from apps.city.models import Review
from apps.user.api.v1.serializers import UserSerializer
from apps.user.models import CustomUser
from core.permissions import IsAdminAccount


@extend_schema(tags=['Admin Panel'])
class AdminBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]


@extend_schema(tags=['Admin Panel: Statistics'])
class AdminStatsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AdminStatsDaily.objects.all().order_by('-day')
    serializer_class = AdminStatsDailySerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminStatsDailyFilter


@extend_schema(tags=['Admin Panel: Businesses'])
class AdminBusinessViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Business.objects.select_related('owner', 'city', 'category').all().order_by('-created_at')
    serializer_class = BusinessSerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminBusinessFilter

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        business = self.get_object()
        business.status = Business.Status.ACTIVE
        business.save(update_fields=['status', 'updated_at'])
        ModerationCase.objects.create(
            entity_type='business',
            entity_id=business.id,
            status=ModerationCase.Status.APPROVED,
            decided_by=request.user,
            decided_at=timezone.now(),
        )
        return Response(self.get_serializer(business).data)

    @action(detail=True, methods=['post'], serializer_class=RejectSerializer)
    def reject(self, request, pk=None):
        business = self.get_object()
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        business.status = Business.Status.REJECTED
        business.save(update_fields=['status', 'updated_at'])
        ModerationCase.objects.create(
            entity_type='business',
            entity_id=business.id,
            status=ModerationCase.Status.REJECTED,
            reason=serializer.validated_data.get('reason', ''),
            decided_by=request.user,
            decided_at=timezone.now(),
        )
        return Response(self.get_serializer(business).data)


@extend_schema(tags=['Admin Panel: Reviews'])
class AdminReviewViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Review.objects.select_related('business', 'user').all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminReviewFilter

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.status = Review.Status.PUBLISHED
        review.save(update_fields=['status'])
        return Response(self.get_serializer(review).data)

    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        review = self.get_object()
        review.status = Review.Status.DELETED
        review.save(update_fields=['status'])
        return Response(self.get_serializer(review).data)


@extend_schema(tags=['Admin Panel: Reports'])
class ReviewReportViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = ReviewReport.objects.select_related('review', 'reporter').all().order_by('-created_at')
    serializer_class = ReviewReportSerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReviewReportFilter

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        report = self.get_object()
        report.status = ReviewReport.Status.RESOLVED
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.save(update_fields=['status', 'resolved_by', 'resolved_at'])
        return Response(self.get_serializer(report).data)


@extend_schema(tags=['Admin Panel: Categories'])
class CategoryViewSet(AdminBaseViewSet):
    queryset = Category.objects.all().order_by('section', 'sort_order', 'name')
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter

    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        category.is_active = False
        category.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Admin Panel: Users'])
class AdminUserViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsAdminAccount]
    filter_backends = [DjangoFilterBackend]
    filterset_class = AdminUserFilter

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        user = self.get_object()
        user.status = CustomUser.Status.BLOCKED
        user.is_active = False
        user.save(update_fields=['status', 'is_active'])
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        user = self.get_object()
        user.status = CustomUser.Status.ACTIVE
        user.is_active = True
        user.save(update_fields=['status', 'is_active'])
        return Response(self.get_serializer(user).data)


@extend_schema(tags=['Admin Panel: Advertising'])
class AdCampaignViewSet(AdminBaseViewSet):
    queryset = AdCampaign.objects.select_related('business', 'city').all().order_by('-created_at')
    serializer_class = AdCampaignSerializer
    filterset_class = AdCampaignFilter


@extend_schema(tags=['Admin Panel: Tariffs'])
class TariffViewSet(AdminBaseViewSet):
    queryset = Tariff.objects.all().order_by('target', 'price_month')
    serializer_class = TariffSerializer
    filterset_class = TariffFilter

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        tariff = self.get_object()
        tariff.is_active = False
        tariff.save(update_fields=['is_active'])
        return Response(self.get_serializer(tariff).data)
