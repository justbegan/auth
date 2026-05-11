from rest_framework import serializers
from django.contrib.gis.geos import Point

from apps.business.models import (
    Business,
    BusinessAnalyticsDaily,
    BusinessLocation,
    BusinessWorkingHours,
    Order,
    OrderItem,
    Product,
    ProductImportJob,
)


class BusinessLocationSerializer(serializers.ModelSerializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)

    class Meta:
        model = BusinessLocation
        exclude = ('point',)

    def _apply_point(self, attrs):
        lat = attrs.pop('lat', serializers.empty)
        lng = attrs.pop('lng', serializers.empty)

        if lat is serializers.empty and lng is serializers.empty:
            return attrs

        current_point = getattr(self.instance, 'point', None)
        if lat is serializers.empty:
            lat = current_point.y if current_point else None
        if lng is serializers.empty:
            lng = current_point.x if current_point else None

        attrs['point'] = None if lat is None or lng is None else Point(float(lng), float(lat), srid=4326)
        return attrs

    def create(self, validated_data):
        validated_data = self._apply_point(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._apply_point(validated_data)
        return super().update(instance, validated_data)


class BusinessWorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessWorkingHours
        fields = '__all__'


class BusinessSerializer(serializers.ModelSerializer):
    locations = BusinessLocationSerializer(many=True, read_only=True)
    working_hours = BusinessWorkingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductImportJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImportJob
        fields = '__all__'
        read_only_fields = ['status', 'total_rows', 'success_rows', 'error_rows', 'errors', 'finished_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class BusinessAnalyticsDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAnalyticsDaily
        fields = '__all__'


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
