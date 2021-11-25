from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PsiViewSet, AirTemperatureViewSet

router = DefaultRouter()
router.register('psi', PsiViewSet, basename="psi")
router.register('air-temperature', AirTemperatureViewSet, basename="air-temperature")

urlpatterns = [
    path('', include(router.urls)),
]