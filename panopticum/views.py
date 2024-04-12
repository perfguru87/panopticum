import os
import django.http
import rest_framework.decorators
import rest_framework.status
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django_filters.rest_framework import DjangoFilterBackend
from functools import wraps

from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import rest_framework.authtoken.models
import django.contrib.auth
import django.contrib.auth.models
import rest_framework.filters

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
    queryset = ComponentVersionModel.history.all().order_by('-id')
    serializer_class = HistoricalComponentVersionSerializer
    filterset_fields = '__all__'


class ComponentViewSet(RelativeURLViewSet):
    queryset = ComponentModel.objects.all()
    serializer_class = ComponentSerializerSimple

    @action(detail=True)
    def latest_version(self, request, pk=None):
        component_obj = self.get_object()
        component_version = ComponentVersionModel.objects.filter(component=component_obj.id).order_by(
            '-update_date').first()
        if not component_version:
            return Response({'error': f"Last version for {component_obj.name}({component_obj.pk}) not found"},
                            status=rest_framework.status.HTTP_404_NOT_FOUND)
        return Response(ComponentVersionSerializerSimple(component_version,
                                                         context={'request': self.request}).data)


class DeploymentLocationClassViewSet(RelativeURLViewSet):
    queryset = DeploymentLocationClassModel.objects.all()
    serializer_class = DeploymentLocationClassSerializer


class ComponentVersionViewSet(viewsets.ModelViewSet):
    queryset = ComponentVersionModel.objects.all().order_by('-id')
    serializer_class = ComponentVersionSerializer
    filterset_class = panopticum.filters.ComponentVersionFilter
    filter_backends = [DjangoFilterBackend]
    filterset_fields = "__all__"
    ordering_fields = ('-version')


class ComponentTypeViewSet(RelativeURLViewSet):
    queryset = ComponentType.objects.all()
    serializer_class = ComponentTypeSerializer


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


class StatusViewSet(viewsets.ModelViewSet):
    queryset = RequirementStatus.objects.all()
    serializer_class = RequirementStatusSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = panopticum.filters.RequirementStatusFilter
    filterset_fields = '__all__'


class RequirementStatusEntryViewSet(RelativeURLViewSet):
    queryset = RequirementStatusEntry.objects.all()
    serializer_class = RequirementStatusEntrySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = panopticum.filters.RequirementStatusEntryFilter
    filterset_fields = '__all__'

    @action(detail=True)
    def history(self, request, pk=None):
        status = self.get_object()
        history_entries = status.history.all().order_by("-history_date")
        page = self.paginate_queryset(history_entries)
        if page is not None:
            serializer = HistoricalRequirementStatusEntrySerializer(page, many=True,
                                                                    context={'request': None})
            return self.get_paginated_response(serializer.data)

        serializer = HistoricalRequirementStatusEntrySerializer(history_entries, many=True,
                                                                context={'request': None})
        return Response(serializer.data)


class RequirementSetViewSet(RelativeURLViewSet):
    queryset = RequirementSet.objects.all().order_by('id')
    serializer_class = RequirementSetSerializer
    filterset_filelds = '__all__'


class UserDetail(RelativeURLViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_class = panopticum.filters.UserFilter
    filterset_fields = ['username', 'email']

    @action(detail=True)
    def photo(self, request, pk=None):
        user = self.get_object()
        if not user.photo:
            return django.http.Http404
        response = django.http.HttpResponse(user.photo.file.read(), content_type='image/jpeg')
        return response


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


def is_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if settings.PAGE_AUTH_REQUIRED:
            return login_required(view_func)(request, *args, **kwargs)
        else:
            return view_func(request, *args, **kwargs)
    return _wrapped_view


@is_login_required
def render_page(request, template, context=None):
    _context = {
        'categories': ComponentCategoryModel.objects.all().order_by('order'),
        'requirementSets': RequirementSet.objects.all().order_by('id'),
        'PAGE_AUTH_REQUIRED': settings.PAGE_AUTH_REQUIRED,
        'JIRA_BASE_URL': os.environ.get('JIRA_URL', '')
    }
    if context:
        _context.update(context)
    return render(request, template, _context)


def component(request):
    return render_page(request, 'page/component.html')


def requirementset(request):
    return render_page(request, 'page/requirementset.html')


def dashboard_components(request):
    return render_page(request, 'dashboard/components.html')


def dashboard_team(request):
    return render_page(request, 'dashboard/team.html')


def techradar_ring(request):
    context = {
        'techradar_infos': TechradarInfo.objects.all().order_by('order'),
        'techradar_rings': TechradarRing.objects.all().order_by('position'),
        'techradar_quadrants': TechradarQuadrant.objects.all().order_by('position')
    }
    return render_page(request, 'techradar/ring.html', context)


def techradar_table(request):
    return render_page(request, 'techradar/table.html')


def techradar_config(request):
    return render_page(request, 'techradar/config.json')


#class JiraIssueView(views.APIView):
#
#    def validate(self, request):
#
#        # FIXME: authentication is required!
#
#        for field in ('URL', 'USER', 'PASSWORD'):
#            if os.environ.get(field, None):
#                raise JsonResponse({'error': '%s environment variable is not congigured' % field},
#                                    safe=False, status=http.client.NOT_IMPLEMENTED)
#
#        if request.method != "GET":
#            return JsonResponse({'error': '%s: method is not allowed' % request.method},
#                                safe=False, status=http.client.METHOD_NOT_ALLOWED)
#
#        return None
#
#    def get(self, request, issue_key):
#        r = self.validate(request)
#        if r:
#            return r
#
#        j = JiraProxy()
#        body, safe, status = j.get_issue(issue_key)
#        return JsonResponse(body, safe=safe, status=status)


class JiraIssueView(viewsets.ModelViewSet):
    queryset = JiraIssue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = (permissions.IsAuthenticated,)


class JiraUrlView(views.APIView):

    def _validate(self, request):
        if request.method != "GET":
            return JsonResponse({'error': '%s: method is not allowed' % request.method},
                                safe=False, status=http.client.METHOD_NOT_ALLOWED)

    def get(self, request):
        r = self._validate(request)
        if r:
            return r

        jira_url = os.environ.get('JIRA_URL', '')
        return JsonResponse({'response': {'jira_url': jira_url}})


class TechradarRingViewSet(RelativeURLViewSet):
    queryset = TechradarRing.objects.all().order_by('position')
    serializer_class = TechradarRingSerializer


class TechradarQuadrantViewSet(RelativeURLViewSet):
    queryset = TechradarQuadrant.objects.all().order_by('position')
    serializer_class = TechradarQuadrantSerializer


class TechradarEntryViewSet(RelativeURLViewSet):
    queryset = TechradarEntry.objects.all()
    serializer_class = TechradarEntrySerializer
