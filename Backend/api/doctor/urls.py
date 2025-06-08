from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DoctorViewSet, SpecialtyViewSet

router = DefaultRouter()
router.register(r'specialties', SpecialtyViewSet)
router.register(r'', DoctorViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 