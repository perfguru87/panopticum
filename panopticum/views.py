from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import *
from .serializers import *


class ProductVersionViewSet(viewsets.ModelViewSet):
    queryset = ProductVersionModel.objects.all().order_by('order')
    serializer_class = ProductVersionSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializer


class ComponentVersionViewSet(viewsets.ModelViewSet):
    queryset = ComponentVersionModel.objects.all()
    serializer_class = ComponentVersionSerializer

    def list(self, request):
        query_set = ComponentVersionModel.objects.all()
        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, url_path='distinct')
    def distinct(self, request, *args, **kwargs):
        query_set = ComponentVersionModel.objects.values('component').distinct()
        serializer = self.get_serializer(query_set, many=True)
        return Response(serializer.data)


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
