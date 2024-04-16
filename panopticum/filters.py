from django_filters import *
from django.db import models
from django.db.models.fields import *
from panopticum import models as panopticum
from django.db.models.fields.related import ForeignObjectRel, ManyToOneRel


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class AutoFilterSet(FilterSet):

    class AutoFilter:
        def __init__(self, models, filter_type, map):
            self.models = models
            self.filter_type = filter_type
            self.map = map

    AUTO_FILTERS = [
        AutoFilter((models.CharField, models.TextField), CharFilter, {'': 'iexact', '__icontains': 'icontains', '__contains': 'contains', '__startswith': 'startswith', '__istartswith': 'istartswith'}),
        AutoFilter((models.IntegerField, models.AutoField, models.ManyToManyField, models.ForeignKey, models.OneToOneField), NumberFilter, {'': 'exact', '__lt': 'lt', '__gt': 'gt'}),
        AutoFilter((models.IntegerField, models.AutoField, models.ManyToManyField), NumberInFilter, {'__in': 'in'}),
        AutoFilter((models.BooleanField,), BooleanFilter, {'': None}),
    ]

    def log(self, msg):
        # import logging
        # logging.info(msg)
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log("-----------------------------")
        self.log("model: %s" % str(self._meta.model))

        model_fields_info = self.traverse_model_fields(self._meta.model)
        for field_name, field in model_fields_info:
            self.filters.update(self.add_filters_for_field(field_name, field))

        self.log(",\n".join(str(a) for a in self.filters.items()))

    def traverse_model_fields(self, model, prefix='', visited_models=None, path=None):
        if path is None:
            path = []

        # Prevent processing a model more than once to avoid infinite loops
        if visited_models is not None:
            if model in visited_models:
                # stop recursion
                return []
            visited_models.add(model)

        if len(path) > 3:
           return []
        if hasattr(model, 'autofilter_do_not_traverse'):
           return []

        fields_info = []

        # for field in model._meta.get_fields(include_parents=True, include_hidden=True):
        for field in model._meta.get_fields(include_hidden=True):
            field_path = '__'.join(path + [field.name]) if path else field.name

            if prefix == '':
                visited_models = set()

            self.log("field: %s|%s (%s)" % (prefix, field.name, field))

            if field.name.endswith("+"):
                self.log("skip 1: %s|%s" % (prefix,field.name))
                continue

            if isinstance(field, (models.ManyToManyField, ManyToOneRel)):
                self.log("skip 3: %s|%s" % (prefix, field.name))
                continue

            if isinstance(field, (models.ForeignKey, models.OneToOneField)):
                # Append the field's own information
                fields_info.append((field_path, field))

                # Continue traversing into the related model
                if hasattr(field, 'related_model'):
                    related_model = field.related_model
                    next_path = path + [field.name] if prefix else [field.name]
                    fields_info.extend(self.traverse_model_fields(related_model, prefix=prefix + field_path, visited_models=visited_models, path=next_path))
            elif isinstance(field, ForeignObjectRel):
                if not field.related_name:
                    # skip inbound references without explicitly defined related name
                    self.log("skip 4: %s|%s" % (prefix, field.name))
                    continue

                if prefix:
                    # skip inbound refernces of second+ order
                    self.log("skip 5: %s|%s " % (prefix, field.name))
                    continue

                related_name = field.get_accessor_name()
                field_path = '__'.join(path + [related_name]) if path else related_name
                # Append the reverse relationship's information
                fields_info.append((field_path, field))

                # Continue traversing into the related model
                related_model = field.related_model
                next_path = path + [related_name] if prefix else [related_name]
                fields_info.extend(self.traverse_model_fields(related_model, prefix=prefix + field_path, visited_models=visited_models, path=next_path))
            else:
                # Handle direct fields
                fields_info.append((field_path, field))

        return fields_info

    def add_filters_for_field(self, field_name, field):
        filters = {}

        for af in self.AUTO_FILTERS:
            for model in af.models:
                if not isinstance(field, model):
                    continue

                for suffix, lookup_expr in af.map.items():
                    if lookup_expr:
                        filters[field_name + suffix] = af.filter_type(field_name=f'{field_name}', lookup_expr=lookup_expr)
                    else:
                        filters[field_name + suffix] = af.filter_type(field_name=f'{field_name}')

                if isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField)):
                    filters[f'{field_name}'] = NumberFilter(field_name=f'{field_name}__id', lookup_expr="exact")
                    filters[f'{field_name}__in'] = NumberInFilter(field_name=f'{field_name}__id', lookup_expr="in")

        return filters


class RequirementFilter(AutoFilterSet):
    class Meta:
        model = panopticum.Requirement
        fields = '__all__'


class UserFilter(AutoFilterSet):
    class Meta:
        model = panopticum.User
        exclude = ('photo', )


class CategoryFilter(AutoFilterSet):
    class Meta:
        model = panopticum.ComponentCategoryModel
        fields = '__all__'


class ComponentFilter(AutoFilterSet):
    class Meta:
        model = panopticum.ComponentModel
        fields = '__all__'


class LocationClassFilter(AutoFilterSet):
    class Meta:
        model = panopticum.DeploymentLocationClassModel
        fields = '__all__'


class DeploymentEnvironmentFilter(AutoFilterSet):
    class Meta:
        model = panopticum.DeploymentEnvironmentModel
        fields = '__all__'


class ProductVersionFilter(AutoFilterSet):
    class Meta:
        model = panopticum.ProductVersionModel
        fields = '__all__'


class RequirementStatusTypeFilter(AutoFilterSet):
    class Meta:
        model = panopticum.RequirementStatusType
        fields = '__all__'


class RequirementStatusFilter(AutoFilterSet):
    class Meta:
        model = panopticum.RequirementStatus
        fields = '__all__'


class RequirementStatusEntryFilter(AutoFilterSet):
    requirementset__ui_slot = NumberFilter(field_name='requirement__sets__ui_slot')

    class Meta:
        model = panopticum.RequirementStatusEntry
        fields = []


class ComponentVersionFilter(AutoFilterSet):
    statuses__requirement = NumberFilter(method='filter_by_requirement')
    deployments__location_class = NumberFilter(field_name='deployments__location_class__id')
    deployments__product_version = NumberFilter(field_name='deployments__product_version__id')
    deployments__is_new_deployment = BooleanFilter(field_name='deployments__is_new_deployment')

    @property
    def qs(self):
        # Ensure the queryset is distinct
        parent = super().qs
        return parent.distinct()

    def filter_by_requirement(self, queryset, name, value):
        get = self.request.GET if self.request else {}

        if 'statuses__status' in get and 'statuses__type' in get:
            q = queryset.filter(statuses__requirement__id=value,
                                statuses__status__id=get.get('statuses__status'),
                                statuses__type__id=get.get('statuses__type')).distinct()
        else:
            q = queryset.filter(statuses__requirement__id=value).distinct()

        return q

    class Meta:
        model = panopticum.ComponentVersionModel
        fields = []
