from rest_framework import serializers

from .models import Psi, AirTemperature


class PsiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Psi
        fields = "__all__"


class AirTemperatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirTemperature
        fields = "__all__"


class SearchDateSerializer(serializers.Serializer):
    date_param = serializers.DateField()
    datetime_param = serializers.DateTimeField()