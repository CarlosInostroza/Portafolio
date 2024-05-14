from django.urls import path, include
from rest_framework import routers
from .views import *

router= routers.DefaultRouter()
router.register('profesional',ProfesionalViewSet)
router.register('cliente',ClienteViewSet)
router.register('administrador',AdministradorViewSet)
urlpatterns = [
    path('', include(router.urls))
]