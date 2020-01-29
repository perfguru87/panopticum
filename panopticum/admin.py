import django.forms
from django.contrib import admin
from django.forms.widgets import SelectMultiple, NumberInput, TextInput, Textarea, Select
import django.contrib.auth.admin
from django.utils.translation import gettext_lazy as _
import django.core.exceptions

import datetime

# Register your models here.
from panopticum.models import *

formfields_large = {models.ForeignKey: {'widget': Select(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '7', 'width': '300px', 'style': 'width:300px'})},
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 60})},
                    }

formfields_small = {models.ForeignKey: {'widget': Select(attrs={'width': '200px', 'style': 'width:200px'})},
                    models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '3', 'width': '150px', 'style': 'width:150px'})},
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '180px', 'style': 'width:180px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 30})},
                    }


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    readonly_fields = ['image', ]
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'title', 'department')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email',
                                         'office_phone', 'mobile_phone', 'image')}),
        (_('Organization'), {'fields': ('organization', 'department', 'role', 'title', 'manager')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    def image(self, obj):
        max_size = 280
        if obj.photo.height < max_size and obj.photo.width < max_size:
            max_size = max(obj.photo.height, obj.photo.width)

        ratio = obj.photo.width / obj.photo.height
        if obj.photo.width >= obj.photo.height:
            width = max_size * ratio
            height = max_size
        else:
            height = max_size /ratio
            width = max_size
        return mark_safe(f'<img src="{obj.photo.url}" width="{width}" height={height} />')


class ComponentDependencyAdmin(admin.TabularInline):
    formfield_overrides = formfields_large
    model = ComponentVersionModel.depends_on.through
    classes = ('collapse', 'no-upper')
    verbose_name = "Component Dependency"
    verbose_name_plural = "Component Dependencies"


class ComponentDeploymentAdmin(admin.TabularInline):
    formfield_overrides = formfields_small
    model = ComponentDeploymentModel
    classes = ('collapse', 'no-upper', 'select-50px')
    verbose_name = "Component Deployment"
    verbose_name_plural = "Component Deployments"



class RequirementAdmin(admin.TabularInline):
    model = Requirement


class RequirementChoiceField(django.forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Requirement: {obj.title}"

class RequirementStatusChoiceField(django.forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"

class RequirementStatusTypeChoiceField(django.forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"Status: {obj.owner}"

class RequirementForm(django.forms.ModelForm):
    requirement = RequirementChoiceField(queryset=Requirement.objects.all()),
    owner_status = RequirementStatusChoiceField(queryset=RequirementStatus.objects.all(),
                                                label='Readiness')
    owner_notes = django.forms.CharField(label='notes',
                                         widget=django.forms.Textarea({'rows': '2'}),
                                         max_length=1024,
                                         required=False)
    approve_status = RequirementStatusChoiceField(queryset=RequirementStatus.objects.all(),
                                                  label='Sign off')
    approve_notes = django.forms.CharField(label='Sign off notes',
                                           widget=django.forms.Textarea({'rows': '2'}),
                                           max_length=1024,
                                           required=False)

    def __init__(self, *args, **kwargs):
        if kwargs.get('instance'):
            initial = {
                'owner_status': kwargs['instance'].status,
                'owner_notes': kwargs['instance'].notes
            }
            try:
                approve_status_obj = RequirementStatusEntry.objects.get(
                    requirement = kwargs['instance'].requirement,
                    type = 2, #approve person
                    component_version = kwargs['instance'].component_version
                )
                initial['approve_status'] = approve_status_obj.status
                initial['approve_notes'] = approve_status_obj.notes
            except django.core.exceptions.ObjectDoesNotExist:
                initial['approve_status'] = RequirementStatus.objects.get(pk=1) # unknown
            kwargs.update(initial=initial)
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if 'requirement' not in self.cleaned_data:
            return True
        return super().is_valid()

    def _save_status(self, field_prefix, type_pk):
        status = self.cleaned_data[f'{field_prefix}_status']
        notes =  self.cleaned_data[field_prefix + "_notes"]
        status_obj, created = RequirementStatusEntry.objects.get_or_create(
            component_version=self.instance.component_version,
            requirement=self.instance.requirement,
            type=RequirementStatusType.objects.get(pk=type_pk),
            defaults={
                "status": status,
                "notes": notes
            }
        )
        if not created:
            status_obj.status = status
            status_obj.notes = notes
            status_obj.save()
        return status_obj

    def save(self, commit=True, *args, **kwargs):
        if 'requirement' in self.cleaned_data:
            if 'approve_status' in self.changed_data or 'approve_notes' in self.changed_data:
                self._save_status('approve', 2)

            elif 'owner_status' in self.changed_data: # reset sign off if readiness is changed
                self.cleaned_data['approve_status'] = RequirementStatus.objects.get(pk=1) # unknown status
                self._save_status('approve', 2)
            return self._save_status('owner', 1)


class RequirementStatusEntryAdmin(admin.TabularInline):
    model = RequirementStatusEntry
    inlines = (RequirementAdmin, )
    form = RequirementForm
    fields = ('requirement', 'owner_status', 'owner_notes','approve_status',  'approve_notes')

    def get_queryset(self, request):
        qs =super().get_queryset(request)
        return qs.filter(type=1) # component owner


    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        field_map = {
            "requirement": RequirementChoiceField(queryset=Requirement.objects.all()),
            "status": RequirementStatusChoiceField(queryset=RequirementStatus.objects.all()),
            "type": RequirementStatusTypeChoiceField(queryset=RequirementStatusType.objects.all())
        }

        if db_field.name in field_map:
            return field_map[db_field.name]
        else:
             return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ComponentVersionAdmin(admin.ModelAdmin):
    formfield_overrides = formfields_large

    inlines = (ComponentDependencyAdmin, ComponentDeploymentAdmin, RequirementStatusEntryAdmin)

    fieldsets = (
        (None, {'fields': ('component', 'version', 'comments')}),
        ('Ownership', {'classes': ('collapse', 'select-200px'),
                       'fields': (
                                  ('owner_maintainer', 'owner_responsible_qa'),
                                  ('owner_product_manager', 'owner_program_manager'),
                                  ('owner_expert', 'owner_escalation_list'), 'owner_architect')}),
        ('Development', {'classes': ('collapse',),
                          'fields': ('dev_language', 'dev_framework', 'dev_database', 'dev_orm', 'dev_logging',
                                     ('dev_raml', 'dev_jira_component'),
                                     ('dev_repo', 'dev_public_repo'),
                                     ('dev_docs', 'dev_public_docs'),
                                     ('dev_build_jenkins_job', 'dev_api_is_public'))}),
        ('Compliance', {'classes': ('collapse', 'show_hide_applicable'),
                          'fields': ('compliance_applicable',
                                     ('compliance_fips_status', 'compliance_fips_notes'),
                                     ('compliance_gdpr_status', 'compliance_gdpr_notes'),
                                     ('compliance_api_status', 'compliance_api_notes'))}),
        ('Operations capabilities', {'classes': ('collapse', 'show_hide_applicable'),
                          'fields': ('op_applicable',
                                     ('op_guide_status', 'op_guide_notes'),
                                     ('op_failover_status', 'op_failover_notes'),
                                     ('op_horizontal_scalability_status', 'op_horizontal_scalability_notes'),
                                     ('op_scaling_guide_status', 'op_scaling_guide_notes'),
                                     ('op_sla_guide_status', 'op_sla_guide_notes'),
                                     ('op_metrics_status', 'op_metrics_notes'),
                                     ('op_alerts_status', 'op_alerts_notes'),
                                     ('op_zero_downtime_status', 'op_zero_downtime_notes'),
                                     ('op_backup_status', 'op_backup_notes'),
                                      'op_safe_restart')}),
        ('Maintenance capabilities', {'classes': ('collapse', 'show_hide_applicable'),
                          'fields': ('mt_applicable',
                                     ('mt_http_tracing_status', 'mt_http_tracing_notes'),
                                     ('mt_logging_completeness_status', 'mt_logging_completeness_notes'),
                                     ('mt_logging_format_status', 'mt_logging_format_notes'),
                                     ('mt_logging_storage_status', 'mt_logging_storage_notes'),
                                     ('mt_logging_sanitization_status', 'mt_logging_sanitization_notes'),
                                     ('mt_db_anonymisation_status', 'mt_db_anonymisation_notes'))}),
        ('Quality Assurance', {'classes': ('collapse', 'show_hide_applicable'),
                          'fields': ('qa_applicable',
                                     ('qa_manual_tests_status', 'qa_manual_tests_notes'),
                                     ('qa_unit_tests_status', 'qa_unit_tests_notes'),
                                     ('qa_e2e_tests_status', 'qa_e2e_tests_notes'),
                                     ('qa_perf_tests_status', 'qa_perf_tests_notes'),
                                     ('qa_security_tests_status', 'qa_security_tests_notes'),
                                     ('qa_longhaul_tests_status', 'qa_longhaul_tests_notes'),
                                     ('qa_api_tests_status', 'qa_api_tests_notes'),
                                     ('qa_anonymisation_tests_status', 'qa_anonymisation_tests_notes'),
                                     ('qa_upgrade_tests_status', 'qa_upgrade_tests_notes'))}),
    )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # standard django method
        if db_field.name in ("owner_product_manager", "owner_program_manager", "owner_expert",
                             "owner_escalation_list", "owner_architect"):
            kwargs["queryset"] = User.objects.filter(hidden=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # standard django method
        if db_field.name in ("owner_maintainer", "owner_responsible_qa"):
            kwargs["queryset"] = User.objects.filter(hidden=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def _clone(self, obj):
        old_depends_on = ComponentDependencyModel.objects.filter(version=obj.id).order_by('id')

        # create new element
        obj.id = None
        obj.save()

        # clone 'ManyToMany & through' relations
        ComponentDependencyModel.objects.bulk_create([ComponentDependencyModel(type=o.type, component=o.component, version=obj, notes=o.notes)
                                                      for o in old_depends_on])

        return obj

    def save_model(self, request, obj, form, change):
        # standard django method
        if obj.pk:
            orig_obj = ComponentVersionModel.objects.get(id=obj.id)
            if orig_obj.version != obj.version:
                obj = self._clone(obj)

        obj.meta_update_date = datetime.datetime.now()
        obj.meta_deleted = False
        super().save_model(request, obj, form, change)

    class Media:
        js = ('/static/js/admin.js',)
        css = {
                  'all': ('/static/css/admin.css',)
              }


admin.site.register(User, UserAdmin)
admin.site.register(CountryModel)
admin.site.register(OrganizationModel)
admin.site.register(OrgDepartmentModel)
admin.site.register(PersonRoleModel)

admin.site.register(SoftwareVendorModel)
admin.site.register(DatabaseVendorModel)
admin.site.register(ProductFamilyModel)
admin.site.register(ProductVersionModel)
admin.site.register(ProgrammingLanguageModel)
admin.site.register(FrameworkModel)
admin.site.register(ORMModel)
admin.site.register(LoggerModel)
admin.site.register(ComponentRuntimeTypeModel)
admin.site.register(ComponentDataPrivacyClassModel)
admin.site.register(ComponentCategoryModel)
admin.site.register(ComponentSubcategoryModel)
admin.site.register(ComponentModel)
admin.site.register(ComponentVersionModel, ComponentVersionAdmin)
admin.site.register(DeploymentLocationClassModel)
admin.site.register(DeploymentEnvironmentModel)
admin.site.register(TCPPortModel)
