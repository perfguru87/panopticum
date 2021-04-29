import django.http
import rest_framework.decorators
import rest_framework.status
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import rest_framework.filters

import panopticum.filters
from .models import *
from .serializers import *

import sys

@login_required
def graph_view(request):
    return render(request, 'graph/graph.html')

def graph_component(request, componentId):
    depth = int(request.GET.get('depth', '1'))
    if (depth < 0):
        depth = 1

    component_version_param = request.GET.get('component_version', None)

    components_list = []
    componentIds_set = set()
    categoryIds_set = set()

    start_component = ComponentModel.objects.get(id=componentId)
    if component_version_param is not None:
        start_component_version = ComponentVersionModel.objects.filter(component=start_component.id, id=int(component_version_param)).first()
    else:
        start_component_version = ComponentVersionModel.objects.filter(component=start_component.id).order_by('-update_date').first()

    # iterate forwards
    process_queue = []
    process_queue.append((start_component, start_component_version))
    for i in range(depth + 1):
        new_process_queue = []
        for (curComponent, curVersion) in process_queue:
            # add component
            if curComponent.id not in componentIds_set:
                componentIds_set.add(curComponent.id)
                components_list.append(make_graph_component(curComponent, curVersion))
                categoryIds_set.add(curComponent.category.id)

            dependency_objects = ComponentDependencyModel.objects.filter(version = curVersion)
            for dependency in curVersion.depends_on.all():
                dependency_object = dependency_objects.filter(component=dependency).first()
                dependency_version = ComponentVersionModel.objects.filter(component=dependency.id).order_by('-update_date').first()
                new_process_queue.append((dependency, dependency_version))

        process_queue = new_process_queue

    # iterate backwards
    process_queue = []
    process_queue.append((start_component, start_component_version))
    for i in range(depth + 1):
        new_process_queue = []
        for (curComponent, curVersion) in process_queue:
            # add component
            if curComponent.id not in componentIds_set:
                componentIds_set.add(curComponent.id)
                components_list.append(make_graph_component(curComponent, curVersion))
                categoryIds_set.add(curComponent.category.id)

            dependents = ComponentDependencyModel.objects.filter(component = curComponent.id) # find components that depends on this version
            for dep in dependents:
                dependency_object = dependents.filter(version=dep.version).first()
                dependency_version = ComponentVersionModel.objects.filter(component=dep.version.component.id).order_by('-update_date').first()
                new_process_queue.append((dep.version.component, dependency_version))

        process_queue = new_process_queue

    # return: component ID, name, parent, forward & backward edges

    response = {
        'components': components_list,
        'categories': get_categories(categoryIds_set)
    }

    return JsonResponse(response)

def get_categories(categoryIds):
    categoriesIds_set = set(categoryIds)
    categories_list = []
    for catId in categoriesIds_set:
        categoryObj = ComponentCategoryModel.objects.filter(id = catId).first()
        categories_list.append({
            "id": catId,
            "name": categoryObj.name
        })

    return categories_list

def make_graph_component(component, component_version):
    # get forward dependencies
    dependsOn_List = []
    dependsOn_DepObjects = ComponentDependencyModel.objects.filter(version = component_version)
    for dependsOn_Component in component_version.depends_on.all():
        dependsOn_Dependency = dependsOn_DepObjects.filter(component = dependsOn_Component).first()
        dependsOn_List.append({
            "id": dependsOn_Component.id,
            "type": dependsOn_Dependency.type
        })

    # get backward dependencies
    dependedUpon_List = []
    dependedUpon_IdSet = set()
    dependendUpon_DepObjects = ComponentDependencyModel.objects.filter(component = component.id)
    for dependedUpon_Dependency in dependendUpon_DepObjects:
        if dependedUpon_Dependency.version.component.id not in dependedUpon_IdSet:
            dependedUpon_IdSet.add(dependedUpon_Dependency.version.component.id)
            dependedUpon_List.append({
                "id": dependedUpon_Dependency.version.component.id
            })

    haReq = RequirementStatusEntry.objects.filter(component_version=component_version.id, requirement=8).first()
    alerts = evaluate_security_alert(component, component_version)

    obj = {
        'id': component.id,
        'name': component.name,
        'category': component.category.id,
        'dependsOn': dependsOn_List,
        'dependedUpon': dependedUpon_List,
        'type': component.type.name,
        'ha': haReq.status.name,
        'sec': alerts,
        "info": {
            "version": component_version.version,
            "desc": component.description,
            "privacy": component.data_privacy_class.name
        }
    }

    return obj

def evaluate_security_alert(component, component_version):
    # rules
    badPorts = [20, 21, 22, 23, 25, 53, 139, 445, 1433, 1434, 3306, 3389]

    alerts = []
    deployments = ComponentDeploymentModel.objects.filter(component_version=component_version.id)
    for deployment in deployments:
        # check ports
        for open_port in deployment.open_ports.all():
            if open_port.port in badPorts:
                alerts.append(f"Vulnerable port {open_port.port} ({open_port.name})")

    return alerts

