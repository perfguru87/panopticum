from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response

from .models import *
from .serializers import *


class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.all().order_by('order')
    serializer_class = ProductSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializer


class ComponentVersionViewSet(viewsets.ModelViewSet):
    queryset = ComponentVersionModel.objects.all()
    serializer_class = ComponentVersionSerializer


class ComponentRuntimeTypeViewSet(viewsets.ModelViewSet):
    queryset = ComponentRuntimeTypeModel.objects.all()
    serializer_class = ComponentRuntimeTypeSerializer


class ComponentDataPrivacyClassViewSet(viewsets.ModelViewSet):
    queryset = ComponentDataPrivacyClassModel.objects.all()
    serializer_class = ComponentDataPrivacyClassSerializer


class ComponentCategoryViewSet(viewsets.ModelViewSet):
    queryset = ComponentCategoryModel.objects.all()
    serializer_class = ComponentCategorySerializer


def component(request):
    return render(request, 'page/component.html')


def dashboard_components(request):
    return render(request, 'dashboard/components.html')
