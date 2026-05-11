from rest_framework import serializers

from apps.admin_panel.models import (
    AdCampaign,
    AdminStatsDaily,
    Category,
    ModerationCase,
    ReviewReport,
    Tariff,
)


class AdminStatsDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminStatsDaily
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ModerationCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationCase
        fields = '__all__'


class ReviewReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReport
        fields = '__all__'


class AdCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdCampaign
        fields = '__all__'


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'


class RejectSerializer(serializers.Serializer):
    reason = serializers.CharField(required=False, allow_blank=True)
