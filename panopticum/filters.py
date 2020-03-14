import rest_framework_filters as filters
from panopticum import models


class RequirementFilter(filters.FilterSet):
    """ allow to filter requirements at REST API side """

    class Meta:
        model = models.Requirement
        fields = '__all__'

class UserFilter(filters.FilterSet):
    username = filters.AutoFilter(lookups='__all__')
    class Meta:
        model = models.User
        exclude = ('photo', )

class CategoryFilter(filters.FilterSet):
    class Meta:
        model = models.ComponentCategoryModel
        fields = '__all__'

class ComponentFilter(filters.FilterSet):
    name = filters.AutoFilter(lookups='__all__')
    category = filters.RelatedFilter(CategoryFilter,
                                     queryset=models.ComponentCategoryModel.objects.all())

    class Meta:
        model = models.ComponentModel
        fields = '__all__'

class LocationClassFilter(filters.FilterSet):
    class Meta:
        model = models.DeploymentLocationClassModel
        fields = '__all__'


class DeploymentEnvironmentFilter(filters.FilterSet):
    class Meta:
        model = models.DeploymentEnvironmentModel
        fields = '__all__'

class ProductVersionFilter(filters.FilterSet):
    class Meta:
        model = models.ProductVersionModel
        fields = '__all__'

class RequirementStatusTypeFilter(filters.FilterSet):

    class Meta:
        model = models.RequirementStatusType
        fields = '__all__'


class RequirementStatusFilter(filters.FilterSet):

    class Meta:
        model = models.RequirementStatus
        fields = '__all__'


class RequirementStatusEntryFilter(filters.FilterSet):
    requirement = filters.RelatedFilter(RequirementFilter,
                                        field_name='requirement',
                                        queryset=models.Requirement.objects.all(),
                                        lookups='__all__')
    component_version = filters.RelatedFilter('ComponentVersionFilter',
                                        field_name='component_version',
                                        queryset=models.ComponentVersionModel.objects.all(),
                                        lookups='__all__')
    status = filters.RelatedFilter(RequirementStatusFilter,
                                   field_name='status',
                                   queryset=models.RequirementStatus.objects.all(),
                                   lookups='__all__')

    class Meta:
        model = models.RequirementStatusEntry
        fields = '__all__'

class DeploymentFilter(filters.FilterSet):
    location_class = filters.RelatedFilter(LocationClassFilter,
                                      field_name='location_class',
                                      queryset=models.DeploymentLocationClassModel.objects.all(),
                                      lookups='__all__')
    environment = filters.RelatedFilter(DeploymentEnvironmentFilter,
                                        field_name='environment',
                                        lookups='__all__',
                                        queryset=models.DeploymentEnvironmentModel.objects.all())
    component_version = filters.RelatedFilter('ComponentVersionFilter',
                                         field_name='component_version',
                                          lookups='__all__',
                                         queryset=models.ComponentVersionModel.objects.all()),
    product_version = filters.RelatedFilter(ProductVersionFilter,
                                            lookups='__all__',
                                            queryset=models.ProductVersionModel.objects.all())

    class Meta:
        model = models.ComponentDeploymentModel
        fields = '__all__'

class ComponentVersionFilter(filters.FilterSet):
    component = filters.RelatedFilter(ComponentFilter,
                                      field_name='component',
                                      queryset=models.ComponentModel.objects.all(),
                                      lookups='__all__')
    owner_maintainer = filters.RelatedFilter(UserFilter,
                                             lookups='__all__',
                                             queryset=models.User.objects.all(),
                                             )
    deployments = filters.RelatedFilter(DeploymentFilter,
                                        field_name='deployments',
                                        queryset=models.ComponentDeploymentModel.objects.all())
    statuses = filters.RelatedFilter(RequirementStatusEntryFilter,
                                     field_name='statuses',
                                     queryset=models.RequirementStatusEntry.objects.all())
    exclude_statuses = filters.BaseInFilter(field_name='statuses',
                                            method='filter_exclude_statuses')
    unknown_status_count = filters.NumberFilter()
    negative_status_count = filters.NumberFilter()
    total_statuses = filters.NumberFilter()
    version = filters.AutoFilter(lookups='__all__')

    class Meta:
        model = models.ComponentVersionModel
        fields = '__all__'

    def filter_exclude_statuses(self, qs, name, value):
        """ handle query params for excluding component version with some requirement statuses.
        that useful for filtering component version that have not requirement statuses by some
        requirement. It's equal to select "unknown" status at frontend filters. We exclude all
        statuses except unknown: Ready, not ready, n/a. That case cover situation when component
        version have not requirement status. If requirement status is not exist it equal "unknown" status"""
        requirement = self.request.query_params.get('exclude_requirement')
        req_type = self.request.query_params.get('exclude_type')
        args = {}
        if requirement:
            args.update({'requirement__in': requirement.split(',')})
        if req_type:
            args.update({'type__in': req_type.split(',')})

        return qs.exclude(statuses__in=models.RequirementStatusEntry.objects.filter(status__in=value, **args))
