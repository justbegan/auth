from rest_framework import serializers
from django.contrib.gis.geos import Point

from apps.board.models import (
    BoardFavorite,
    BoardListing,
    BoardListingAttribute,
    BoardListingMedia,
    BoardListingStatsDaily,
    BoardReport,
)


class BoardListingMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardListingMedia
        fields = '__all__'


class BoardListingAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardListingAttribute
        fields = '__all__'


class BoardListingSerializer(serializers.ModelSerializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    lng = serializers.DecimalField(max_digits=9, decimal_places=6, required=False, allow_null=True)
    media = BoardListingMediaSerializer(many=True, read_only=True)
    attributes = BoardListingAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = BoardListing
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


class BoardFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardFavorite
        fields = '__all__'


class BoardListingStatsDailySerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardListingStatsDaily
        fields = '__all__'


class BoardReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoardReport
        fields = '__all__'
