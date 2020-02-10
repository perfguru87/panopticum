import rest_framework_filters as filters
from panopticum import models


class RequirementFilter(filters.FilterSet):
    """ allow to filter requirements at REST API side """

    class Meta:
        model = models.Requirement
        fields = '__all__'

class ComponentVersionFilter(filters.FilterSet):
    class Meta:
        model = models.ComponentVersionModel
        fields = '__all__'

class RequirementStatusFilter(filters.FilterSet):
    requirement = filters.RelatedFilter(RequirementFilter,
                                        field_name='requirement',
                                        queryset=models.Requirement.objects.all())
    component_version = filters.RelatedFilter(ComponentVersionFilter,
                                        field_name='component_version',
                                        queryset=models.ComponentVersionModel.objects.all())

    class Meta:
        model = models.RequirementStatusEntry
        fields = '__all__'
