import rest_framework_filters as filters
from panopticum import models


class RequirementTypeFilter(filters.FilterSet):
    class Meta:
        model = models.RequirementType
        fields = '__all__'


class RequirementFilter(filters.FilterSet):
    type = filters.RelatedFilter(RequirementTypeFilter,
                                 field_name='type',
                                 queryset=models.RequirementType.objects.all())

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
