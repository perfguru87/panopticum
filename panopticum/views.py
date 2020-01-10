from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import views

from .models import *
from .serializers import *
from .jira import JiraProxy


class ProductVersionViewSet(viewsets.ModelViewSet):
    queryset = ProductVersionModel.objects.all().order_by('order')
    serializer_class = ProductVersionSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializer


class DeploymentLocationClassViewSet(viewsets.ModelViewSet):
    queryset = DeploymentLocationClassModel.objects.all()
    serializer_class = DeploymentLocationClassSerializer


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


class JiraIssueView(views.APIView):

    def validate(self, request):

        # FIXME: authentication is required!

        for field in ('URL', 'USER', 'PASSWORD'):
            if field not in settings.JIRA_CONFIG:
                raise JsonResponse({'error': 'JIRA_CONFIG.%s setting is not congigured' % field},
                                    safe=False, status=http.client.NOT_IMPLEMENTED)

        if request.method != "GET":
            return JsonResponse({'error': '%s: method is not allowed' % request.method},
                                safe=False, status=http.client.METHOD_NOT_ALLOWED)

        return None

    def get(self, request, issue_key):
        r = self.validate(request)
        if r:
            return r

        j = JiraProxy()
        body, safe, status = j.get_issue(issue_key)
        return JsonResponse(body, safe=safe, status=status)


class JiraUrlView(views.APIView):

    def _validate(self, request):
        if request.method != "GET":
            return JsonResponse({'error': '%s: method is not allowed' % request.method},
                                safe=False, status=http.client.METHOD_NOT_ALLOWED)

    def get(self, request):
        r = self._validate(request)
        if r:
            return r

        return JsonResponse({'response': {'jira_url': settings.JIRA_CONFIG.get('URL', '')}})
