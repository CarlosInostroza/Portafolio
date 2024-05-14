from rest_framework import serializers
from app.models import *
from django.core.files import File
import os

class ProfesionalSerializer (serializers.ModelSerializer):
    class Meta:
        model = Profesional
        fields = '__all__'

class ClienteSerializer (serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ('__all__')

class AdministradorSerializer (serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = '__all__'
