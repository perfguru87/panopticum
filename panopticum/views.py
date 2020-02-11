import rest_framework.decorators
import rest_framework.status
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse

from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import rest_framework.authtoken.models
import django.contrib.auth
import django.contrib.auth.models

import panopticum.filters
from .models import *
from .serializers import *
from .jira import JiraProxy

class RelativeURLViewSet(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': None})
        return context

class ProductVersionViewSet(RelativeURLViewSet):
    queryset = ProductVersionModel.objects.all().order_by('order')
    serializer_class = ProductVersionSerializer

class HistoryComponentVersionViewSet(RelativeURLViewSet):
    queryset = ComponentVersionModel.history.all()
    serializer_class = HistoricalComponentVersionSerializer
    filterset_fields = '__all__'


class ComponentViewSet(RelativeURLViewSet):
    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializerSimple

    @action(detail=True)
    def latest_version(self, request, pk=None):
        component_obj = self.get_object()
        component_version = ComponentVersionModel.objects.filter(component=component_obj.id).order_by(
            '-meta_update_date').first()
        if not component_version:
            return Response({'error': f"Last version for {component_obj.name}({component_obj.pk}) not found"},
                            status=rest_framework.status.HTTP_404_NOT_FOUND)
        return Response(ComponentVersionSerializerSimple(component_version,
                                                         context={'request': self.request}).data)

class DeploymentLocationClassViewSet(RelativeURLViewSet):
    queryset = DeploymentLocationClassModel.objects.all()
    serializer_class = DeploymentLocationClassSerializer


class ComponentVersionViewSet(RelativeURLViewSet):
    queryset = ComponentVersionModel.objects.all()
    serializer_class = ComponentVersionSerializer
    filterset_fileds = "__all__"


class ComponentRuntimeTypeViewSet(RelativeURLViewSet):
    queryset = ComponentRuntimeTypeModel.objects.all()
    serializer_class = ComponentRuntimeTypeSerializer


class ComponentDataPrivacyClassViewSet(RelativeURLViewSet):
    queryset = ComponentDataPrivacyClassModel.objects.all()
    serializer_class = ComponentDataPrivacyClassSerializer


class ComponentCategoryViewSet(RelativeURLViewSet):
    queryset = ComponentCategoryModel.objects.all()
    serializer_class = ComponentCategorySerializer


class RequirementViewSet(RelativeURLViewSet):
    queryset = Requirement.objects.all()
    serializer_class = RequirementSerializer
    filter_class = panopticum.filters.RequirementFilter
    filterset_fields = '__all__'


class RequirementStatusViewSet(RelativeURLViewSet):
    queryset = RequirementStatusEntry.objects.all()
    serializer_class = RequirementStatusEntrySerializer
    filter_class = panopticum.filters.RequirementStatusFilter
    filterset_fields = '__all__'

    @action(detail=True)
    def history(self, request, pk=None):
        status = self.get_object()
        history_entries = status.history.all()
        page = self.paginate_queryset(history_entries)
        if page is not None:
            serializer = HistoricalRequirementStatusEntrySerializer(page, many=True,
                                                                    context={'request': None})
            return self.get_paginated_response(serializer.data)

        serializer = HistoricalRequirementStatusEntrySerializer(history_entries, many=True,
                                                                context={'request': None})
        return Response(serializer.data)


class RequirementSetViewSet(RelativeURLViewSet):
    queryset = RequirementSet.objects.all()
    serializer_class = RequirementSetSerializer
    filterset_filelds = '__all__'


class UserDetail(RelativeURLViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filterset_fields = ['username', 'email']


class Token(RelativeURLViewSet):
    queryset = rest_framework.authtoken.models.Token.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.IsAuthenticated,)


class LoginAPIView(APIView):

    def get(self, request, format=None):
        if not isinstance(request.user, django.contrib.auth.models.AnonymousUser):
            content = {
                'id': request.user.id,
                'user': request.user.username,  # `django.contrib.auth.User` instance.
                'is_authenticated': request.user.is_authenticated,
                'auth': request.auth
            }
            return Response(content)
        else:
            return Response({"error": "not logged in"}, 401)

    def post(self, request):
        user = django.contrib.auth.authenticate(request,
                                                username=request.data['username'],
                                                password=request.data['password'])
        if user:
            django.contrib.auth.login(request, user)
            return Response({
                "username": user.username,
                "token": rest_framework.authtoken.models.Token.objects.get_or_create(user=request.user)[0].key
            })
        else:
            return Response({"error": "not valid credentials"}, 401)


def component(request):
    return render(request, 'page/component.html')


def dashboard_components(request):
    return render(request, 'dashboard/components.html')


def dashboard_operations(request):
    return render(request, 'dashboard/operations.html')


def dashboard_quality_assurance(request):
    return render(request, 'dashboard/quality_assurance.html')


def dashboard_maintenance(request):
    return render(request, 'dashboard/maintenance.html')


def dashboard_compliance(request):
    return render(request, 'dashboard/compliance.html')


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
