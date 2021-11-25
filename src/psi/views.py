from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Max

from rest_framework import pagination, status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, permission_classes

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Psi, AirTemperature
from .serializers import PsiSerializer, AirTemperatureSerializer, SearchDateSerializer
from .decorators import validate_datetime


class PsiPagination(pagination.PageNumberPagination):
    page_size = 100
    max_page_size = 200
    page_query_param = "p"
    page_size_query_param = "count"


class PsiViewSet(ModelViewSet):
    serializer_class = PsiSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PsiPagination
    queryset = Psi.objects.all()

    @swagger_auto_schema(request_body=SearchDateSerializer)
    @action(methods=['POST'], detail=False)
    @validate_datetime
    def search(self, request, *args, **kwargs):
        req = kwargs['param']

        if req.get('type') == "date":
            data = Psi.objects.filter(updated_timestamp__date=req.get("value"))
        elif req.get("type") == "datetime":
            data = Psi.objects.filter(updated_timestamp=req.get("value"))

        if not data.exists():
            data = Psi.objects.filter(updated_timestamp=Psi.objects.aggregate(max_date=Max("updated_timestamp"))['max_date'])

        return JsonResponse(list(data.values()), safe=False, status=status.HTTP_200_OK)


class AirTemperatureViewSet(ViewSet):
    serializer_class = AirTemperatureSerializer
    permission_classes = (IsAuthenticated,)

    count = openapi.Parameter("page size", openapi.IN_QUERY, description="page size", type=openapi.TYPE_INTEGER)
    p = openapi.Parameter("page number", openapi.IN_QUERY, description="page number", type=openapi.TYPE_INTEGER)    

    @swagger_auto_schema(manual_parameters=[count, p])
    def list(self, request):
        air_temperatures = AirTemperature.objects.all()
        count = request.GET.get('page size', 100)
        p = request.GET.get('page number', 1)
        paginator = Paginator(air_temperatures, count)
        return JsonResponse(list(paginator.page(p).object_list.values()), safe=False, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(air_temperature)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)
    def update(self, request, pk):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(air_temperature, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(request_body=AirTemperatureSerializer)
    def partial_update(self, request, pk):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        serializer = self.serializer_class(air_temperature, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def destroy(self, request, pk):
        air_temperature = get_object_or_404(AirTemperature, pk=pk)
        air_temperature.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=SearchDateSerializer)
    @action(methods=['POST'], detail=False)
    @validate_datetime
    def search(self, request, *args, **kwargs):
        req = kwargs['param']

        if req.get('type') == "date":
            data = AirTemperature.objects.filter(timestamp__date=req.get("value"))
        elif req.get("type") == "datetime":
            data = AirTemperature.objects.filter(timestamp=req.get("value"))

        if not data.exists():
            data = AirTemperature.objects.filter(timestamp__date=AirTemperature.objects.aggregate(max_date=Max("timestamp"))['max_date'].date())

        return JsonResponse(list(data.values()), safe=False, status=status.HTTP_200_OK)