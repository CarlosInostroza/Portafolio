from rest_framework import viewsets
from .serializer import *
from app.models import *

class ProfesionalViewSet(viewsets.ModelViewSet):
    queryset = Profesional.objects.all()
    serializer_class=ProfesionalSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class=ClienteSerializer

class AdministradorViewSet(viewsets.ModelViewSet):
    queryset = Administrador.objects.all()
    serializer_class=AdministradorSerializer