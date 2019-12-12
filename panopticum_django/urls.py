"""panopticum URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include

from rest_framework import routers

from panopticum import views

router = routers.DefaultRouter()
router.register(r'product', views.ProductViewSet)
router.register(r'component_version', views.ComponentVersionViewSet)
router.register(r'component_category', views.ComponentCategoryViewSet)
router.register(r'component_runtime_type', views.ComponentRuntimeTypeViewSet)
router.register(r'component_location_class', views.ComponentLocationClassViewSet)
router.register(r'component_data_privacy_class', views.ComponentDataPrivacyClassViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    url('^component/', views.component, name='Component'),
    url('^dashboard/components.html', views.dashboard_components, name='Components'),
    url('^dashboard/links.html', views.dashboard_components, name='Links'),
    url('^api/', include(router.urls)),
    url('', views.dashboard_components, name='Components')
]
