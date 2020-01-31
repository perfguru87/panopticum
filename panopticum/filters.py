import rest_framework_filters as filters
from panopticum import models


class RequirementFilter(filters.FilterSet):

    class Meta:
        model = models.Requirement
        fields = '__all__'


class RequirementStatusFilter(filters.FilterSet):
    requirement = filters.RelatedFilter(RequirementFilter,
                                        field_name='requirement',
                                        queryset=models.Requirement.objects.all())

    class Meta:
        model = models.RequirementStatusEntry
        fields = '__all__'
