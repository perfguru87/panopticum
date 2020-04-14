import typing

import django.forms
from django.contrib import admin
from django.forms.widgets import SelectMultiple, NumberInput, TextInput, Textarea, Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import django.core.exceptions
from django.contrib.auth.models import AnonymousUser

# Register your models here.
import panopticum.fields
from panopticum.models import *

SIGNEE_STATUS_TYPE = 2 # Requirement status type with name = "approver person". Check init.json
OWNER_STATUS_TYPE = 1
UNKNOWN_REQUIREMENT_STATUS = 1 # it's unknown status. Check init.json fixture
OWNER_STATUS_PERMISSION = 'panopticum.change_owner_status'
SIGNEE_STATUS_PERMISSION = 'panopticum.change_signee_status'

formfields_large = {models.ForeignKey: {'widget': Select(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '7', 'width': '300px', 'style': 'width:300px'})},
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 60})},
                    }

formfields_small = {models.ForeignKey: {'widget': Select(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '3', 'width': '150px', 'style': 'width:150px'})},
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 30})},
                    }


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    readonly_fields = ['image', ]
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'title', 'department')
    change_form_template = 'loginas/change_form.html'

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


class RequirementInlineAdmin(admin.TabularInline):
    model = Requirement


class RequirementForm(django.forms.ModelForm):
    """ Custom admin form for Requirement row. We merge 2 requirement statuses to Requirement row.
    Pay attention: we does not have model for Requirement row. We do not need it until we can calculate it
    from requirement statues by django admin form and frontend """
    owner_status = panopticum.fields.RequirementStatusChoiceField(queryset=RequirementStatus.objects.all(),
                                                                  label='Readiness')
    owner_notes = django.forms.CharField(label='notes',
                                         widget=django.forms.Textarea({'rows': '2'}),
                                         max_length=16 * pow(2, 10),
                                         required=False,
                                         )
    approve_status = panopticum.fields.RequirementStatusChoiceField(
        queryset=RequirementStatus.objects.filter(allow_for=SIGNEE_STATUS_TYPE),
        label='Sign off'
    )
    approve_notes = django.forms.CharField(label='Signee notes',
                                           widget=django.forms.Textarea({'rows': '2'}),
                                           max_length=16 * pow(2, 10),
                                           required=False)
    user = AnonymousUser()

    class Meta:
        fields = '__all__'
        model = RequirementStatusEntry
        labels = {
            'owner_status': 'Readiness',
            'owner_notes': 'Notes',
            'approve_status': 'Sign off',
            'approve_notes': 'Sign off notes'
        }

    def __init__(self, *args, **kwargs):

        # define initial fields values
        self.base_fields['owner_status'].initial = UNKNOWN_REQUIREMENT_STATUS
        self.base_fields['approve_status'].initial = UNKNOWN_REQUIREMENT_STATUS

        if kwargs.get('instance'):
            # read and set field values from status models
            initial = {
                'owner_status': kwargs['instance'].status.pk,
                'owner_notes': kwargs['instance'].notes
            }
            try:
                signee_status_obj = self.get_signee_status(kwargs['instance'])
                initial['approve_status'] = signee_status_obj.status.pk
                initial['approve_notes'] = signee_status_obj.notes
            except django.core.exceptions.ObjectDoesNotExist:
                # set default values for signee
                initial['approve_status'] = UNKNOWN_REQUIREMENT_STATUS

            kwargs.update(initial=initial)

        super().__init__(*args, **kwargs)

        if 'instance' in kwargs:  # disable defined requirement. We disallow to change requirement title after save
            self.fields['requirement'].disabled = True
        if not self.user.has_perm(OWNER_STATUS_PERMISSION):
            self.fields['owner_status'].disabled = True
            self.fields['owner_notes'].disabled = True
        if not self.user.has_perm(SIGNEE_STATUS_PERMISSION):
            self.fields['approve_status'].disabled = True
            self.fields['approve_notes'].disabled = True

    @staticmethod
    def get_signee_status(obj):
        return RequirementStatusEntry.objects.get(
            requirement=obj.requirement,
            type=SIGNEE_STATUS_TYPE,
            component_version=obj.component_version
        )

    def is_valid(self):
        # skip validation for 3 empty requirement rows that added bellow
        if 'requirement' not in self.cleaned_data:
            return True
        return super().is_valid()

    def _save_status(self, field_prefix, type_pk):
        status = self.cleaned_data[f'{field_prefix}_status']
        notes = self.cleaned_data[field_prefix + "_notes"]
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
                self._save_status('approve', SIGNEE_STATUS_TYPE)

            elif 'owner_status' in self.changed_data:  # reset sign off if readiness is changed
                self.cleaned_data['approve_status'] = RequirementStatus.objects.get(pk=UNKNOWN_REQUIREMENT_STATUS)
                self._save_status('approve', SIGNEE_STATUS_TYPE)
            return self._save_status('owner', OWNER_STATUS_TYPE)


class RequirementStatusEntryAdmin(admin.TabularInline):
    model = RequirementStatusEntry
    form = RequirementForm
    fields = ('requirement', 'owner_status', 'owner_notes', 'approve_status', 'approve_notes')
    classes = ('collapse', 'requirements-admin', 'no-upper')
    extra = 1
    verbose_name_plural = "Requirements"

    def requirement(self, obj):
        return obj.name

    def owner_status(self, obj):
        return obj.status.name

    def owner_notes(self, obj):
        return obj.notes

    def approve_status(self, obj):
        return self.form.get_signee_status(obj).status.name

    def approve_notes(self, obj):
        return self.form.get_signee_status(obj).notes

    def get_formset(self, request, obj=None, **kwargs):
        self.form.user = request.user
        return super().get_formset(request, obj, **kwargs)

    def get_queryset(self, request):
        qs =super().get_queryset(request)
        # show requirements available for requirement set owners only
        if not request.user.has_perm(OWNER_STATUS_PERMISSION) and \
                request.user.has_perm(SIGNEE_STATUS_PERMISSION):
            return qs.filter(type=SIGNEE_STATUS_TYPE,
                             requirement__sets__owner_groups__in=request.user.groups.all()).order_by('requirement_id')
        return qs.filter(type=OWNER_STATUS_TYPE).order_by('requirement_id')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        requirement_qs = Requirement.objects.all()
        # choice list must contain only requirements available for requirement set owners
        if not request.user.has_perm(OWNER_STATUS_PERMISSION) and \
                request.user.has_perm(SIGNEE_STATUS_PERMISSION):
            requirement_qs = requirement_qs.filter(sets__owner_groups__in=request.user.groups.all())

        field_map = {
            "requirement": panopticum.fields.RequirementChoiceField(
                queryset=requirement_qs
            ),
        }

        if db_field.name in field_map:
            return field_map[db_field.name]
        else:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        """ Allow change requirement if user have permissions """
        return request.user.has_perm(SIGNEE_STATUS_PERMISSION) or \
               (request.user.has_perm(OWNER_STATUS_PERMISSION) and
                obj and request.user == obj.owner_maintainer)

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

class RequirementAdmin(admin.ModelAdmin):
    list_display = ['title']
    model = Requirement


class RequirementSetAdmin(admin.ModelAdmin):
    filter_horizontal = ['requirements', 'owner_groups']
    list_display = ['name']
    model = RequirementSet


class ComponentVersionAdmin(admin.ModelAdmin):
    formfield_overrides = formfields_large
    search_fields = ['component__name', 'version']
    autocomplete_fields = ['owner_maintainer',
                           'owner_responsible_qa',
                           'owner_product_manager',
                           'owner_program_manager',
                           'owner_expert',
                           'owner_escalation_list',
                           'owner_architect']

    inlines = (ComponentDependencyAdmin, ComponentDeploymentAdmin, RequirementStatusEntryAdmin)

    fieldsets = [
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
    ]

    @staticmethod
    def _has_perm_by_component_person(obj, user, action):
        perm_person_map = {
            f'panopticum.escalation_list_{action}': obj.owner_escalation_list,
            f'panopticum.architect_{action}': obj.owner_architect,
            f'panopticum.experts_{action}': obj.owner_expert,
            f'panopticum.qa_{action}': obj.owner_responsible_qa,
            f'panopticum.program_manager_{action}': obj.owner_program_manager,
            f'panopticum.product_manager_{action}': obj.owner_product_manager
        }
        for perm, person_set in perm_person_map.items():

            if isinstance(person_set, User):
                if user == person_set:
                    return True
                else:
                    continue
            elif person_set and user.has_perm(perm) and person_set.filter(pk=user.pk).exists():
                return True

    def has_change_permission(self, request, obj: typing.Optional[ComponentVersionModel]=None):
        return request.user.is_superuser or \
               (obj and request.user == obj.owner_maintainer) or \
               (obj and self._has_perm_by_component_person(obj, request.user, 'change')) or \
               request.user.has_perm(SIGNEE_STATUS_PERMISSION)

    def has_delete_permission(self, request, obj: typing.Optional[ComponentVersionModel]=None):
        return request.user.is_superuser or \
               (obj and request.user == obj.owner_maintainer) or \
               (obj and self._has_perm_by_component_person(obj, request.user, 'delete'))

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = set(super().get_readonly_fields(request, obj))

        if request.user.has_perm(SIGNEE_STATUS_PERMISSION) and not request.user.is_superuser:
            for title, definition in self.get_fieldsets(request, obj):
                readonly_fields.update(definition.get('fields', ()))
        return tuple(readonly_fields)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # standard django method
        if db_field.name in ("owner_product_manager", "owner_program_manager", "owner_expert",
                             "owner_escalation_list", "owner_architect"):
            kwargs["queryset"] = User.objects.filter(hidden=False)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ("owner_maintainer", "owner_responsible_qa"):
            kwargs["queryset"] = User.objects.filter(hidden=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        """ allow to edit requirements if user have permission panopticum.change_*_status and
        ignore change_component_version_model permission.
        """
        can_edit_parent = self.has_change_permission(request, obj) if obj else self.has_add_permission(request)
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            if can_edit_parent or issubclass(formset.model, RequirementStatusEntry):
                has_add_permission = inline._has_add_permission(request, obj)
                has_change_permission = inline.has_change_permission(request, obj)
                has_delete_permission = inline.has_delete_permission(request, obj)

            else:
                # Disable all edit-permissions, and overide formset settings.
                has_add_permission = has_change_permission = has_delete_permission = False
                formset.extra = formset.max_num = 0
            has_view_permission = inline.has_view_permission(request, obj)
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = admin.helpers.InlineAdminFormSet(
                inline, formset, fieldsets, prepopulated, readonly, model_admin=self,
                has_add_permission=has_add_permission, has_change_permission=has_change_permission,
                has_delete_permission=has_delete_permission,
                has_view_permission=has_view_permission,
            )
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets


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
admin.site.register(RuntimeModel)
admin.site.register(ORMModel)
admin.site.register(LoggerModel)
admin.site.register(ComponentType)
admin.site.register(ComponentDataPrivacyClassModel)
admin.site.register(ComponentCategoryModel)
admin.site.register(ComponentSubcategoryModel)
admin.site.register(ComponentModel)
admin.site.register(ComponentVersionModel, ComponentVersionAdmin)
admin.site.register(DeploymentLocationClassModel)
admin.site.register(DeploymentEnvironmentModel)
admin.site.register(TCPPortModel)
admin.site.register(RequirementSet, RequirementSetAdmin)
admin.site.register(Requirement, RequirementAdmin)
