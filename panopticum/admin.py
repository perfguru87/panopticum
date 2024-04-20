import typing

import django.contrib.admin.sites
import django.forms
from django.contrib import admin
from django.forms.widgets import SelectMultiple, NumberInput, TextInput, Textarea, Select
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import django.core.exceptions
from django.contrib.auth.models import AnonymousUser
from django.forms.widgets import CheckboxSelectMultiple

# Register your models here.
import panopticum.fields
from panopticum.models import *

OWNER_STATUS_PERMISSION = 'panopticum.change_owner_status'
SIGNEE_STATUS_PERMISSION = 'panopticum.change_signee_status'

formfields_large = {
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 60})},
                    }

formfields_small = {
                    models.IntegerField: {'widget': NumberInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.CharField: {'widget': TextInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.URLField: {'widget': TextInput(attrs={'width': '150px', 'style': 'width:150px'})},
                    models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 30})},
                    }


class UserAdmin(django.contrib.auth.admin.UserAdmin):
    readonly_fields = ['image', ]
    list_display = ('username', 'first_name', 'last_name', 'is_staff', 'title', 'department')
    change_form_template = 'loginas/change_form.html'
    search_fields = ('username', 'first_name', 'last_name')

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


class TCPPortAdmin(admin.ModelAdmin):
    search_fields = ['port', ]
    ordering = ['port', ]
    model = TCPPortModel


class ComponentDeploymentAdmin(admin.TabularInline):
    formfield_overrides = formfields_small
    model = ComponentDeploymentModel
    classes = ('collapse', 'no-upper', 'select-50px')
    verbose_name = "Component Deployment"
    verbose_name_plural = "Component Deployments"
    autocomplete_fields = ['open_ports', ]


class ProductFamilyAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name']
    model = ProductFamilyModel


class ProductVersionAdmin(admin.ModelAdmin):
    model = ProductVersionModel
    search_fields = ['name', 'shortname']
    # Exclude showing status since there is no release permission to check with
    exclude = ('status',)


class LanguageAdmin(admin.ModelAdmin):
    model = ProgrammingLanguageModel
    search_fields = ["name", ]


class FrameworkAdmin(admin.ModelAdmin):
    model = FrameworkModel
    search_fields = ['name', ]


class DatabaseAdmin(admin.ModelAdmin):
    model = DatabaseVendorModel
    search_fields = ['name', ]


class ORMAdmin(admin.ModelAdmin):
    model = ORMModel
    search_fields = ['name', ]


class LoggerAdmin(admin.ModelAdmin):
    model = LoggerModel
    search_fields = ['name', ]


class RuntimeAdmin(admin.ModelAdmin):
    model = RuntimeModel
    search_fields = ['name', ]


class RequirementInlineAdmin(admin.TabularInline):
    model = Requirement


class RequirementForm(django.forms.ModelForm):
    """ Custom admin form for Requirement row. We merge 2 requirement statuses to Requirement row.
    Pay attention: we does not have model for Requirement row. We do not need it until we can calculate it
    from requirement statues by django admin form and frontend """
    owner_status = panopticum.fields.RequirementStatusChoiceField(queryset=RequirementStatus.objects.
                                                                  filter(allow_for=REQ_OWNER_STATUS),
                                                                  label='Readiness')
    owner_notes = django.forms.CharField(label='notes',
                                         widget=django.forms.Textarea({'rows': '2'}),
                                         max_length=16 * pow(2, 10),
                                         required=False,
                                         )
    approve_status = panopticum.fields.RequirementStatusChoiceField(
        queryset=RequirementStatus.objects.filter(allow_for=REQ_SIGNEE_STATUS),
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
        self.base_fields['owner_status'].initial = REQ_STATUS_UNKNOWN
        self.base_fields['approve_status'].initial = REQ_STATUS_UNKNOWN

        if kwargs.get('instance'):
            # read and set field values from status models
            owner_status_obj = self.get_status(kwargs['instance'], REQ_OWNER_STATUS)
            initial = {
                'owner_status': owner_status_obj.status.pk,
                'owner_notes': owner_status_obj.notes
            }
            try:
                signee_status_obj = self.get_status(kwargs['instance'], REQ_SIGNEE_STATUS)
                initial['approve_status'] = signee_status_obj.status.pk
                initial['approve_notes'] = signee_status_obj.notes
            except django.core.exceptions.ObjectDoesNotExist:
                # set default values for signee
                initial['approve_status'] = REQ_STATUS_UNKNOWN

            kwargs.update(initial=initial)

        super().__init__(*args, **kwargs)

        # disable defined requirement. We disallow to change requirement title after save
        if 'instance' in kwargs:
            self.fields['requirement'].disabled = True
        if not self.user.has_perm(OWNER_STATUS_PERMISSION):
            self.fields['owner_status'].disabled = True
            self.fields['owner_notes'].disabled = True
        if not self.user.has_perm(SIGNEE_STATUS_PERMISSION):
            self.fields['approve_status'].disabled = True
            self.fields['approve_notes'].disabled = True

    @staticmethod
    def get_status(obj, status_type=REQ_OWNER_STATUS):
        return RequirementStatusEntry.objects.get(
            requirement=obj.requirement,
            type=status_type,
            component_version=obj.component_version
        )

    def is_valid(self):
        # If maintainer is changed, reset list of errors, retrieve statuses from previous maintainer
        # and re-validate form
        if self._ownership_changed():
            self._errors = None
            self.data[self.add_prefix('owner_status')] = self.initial.get('owner_status') or \
                                                         self.base_fields['owner_status'].initial
            self.data[self.add_prefix('owner_notes')] = self.initial.get('owner_notes')

            self.data[self.add_prefix('approve_status')] = self.initial.get('approve_status') or \
                                                           self.base_fields['approve_status'].initial
            self.data[self.add_prefix('approve_notes')] = self.initial.get('approve_notes')
            self.full_clean()
            # Append maintainer to changed data array to save approve status
            self.ownership_is_changed = True

        # skip validation for 3 empty requirement rows that added bellow
        if 'requirement' not in self.cleaned_data:
            return True
        return super().is_valid()

    def _ownership_changed(self):
        if not hasattr(self.instance, 'component_version') or not getattr(self.instance.component_version, 'id', 0):
            return
        component_version = ComponentVersionModel.objects.get(id=self.instance.component_version.id)

        changed_owner_maintainer_id = int(self.data.get('owner_maintainer', 0) or 0)
        original_owner_maintainer_id = getattr(component_version.owner_maintainer, 'id', 0)

        changed_owner_responsible_qa_id = int(self.data.get('owner_responsible_qa', 0) or 0)
        original_owner_responsible_qa_id = getattr(component_version.owner_responsible_qa, 'id', 0)

        return original_owner_maintainer_id != changed_owner_maintainer_id or \
               original_owner_responsible_qa_id != changed_owner_responsible_qa_id

    def _save_status(self, field_prefix, type_pk):
        status = self.cleaned_data[f'{field_prefix}_status']
        notes = self.cleaned_data[field_prefix + "_notes"]
        obj, created = RequirementStatusEntry.objects.get_or_create(
            component_version=self.instance.component_version,
            requirement=self.instance.requirement,
            type=RequirementStatusType.objects.get(pk=type_pk),
            defaults={
                "status": status,
                "notes": notes
            }
        )
        if not created:
            obj.status = status
            obj.notes = notes
            obj.save()

        return obj

    def _save_overall_status(self, owner_status, signee_status):
        status = REQ_STATUS_UNKNOWN
        msg = "?"

        if owner_status.status.id in (REQ_STATUS_READY, REQ_STATUS_NOT_APPLICABLE):
            if not signee_status or not signee_status.status or not signee_status.status.id or signee_status.status.id == REQ_STATUS_UNKNOWN:
                msg = "Waiting for approval..."
                if owner_status.status.id == REQ_STATUS_NOT_APPLICABLE:
                    status = REQ_STATUS_WAITING_FOR_NA_APPROVAL
                else:
                    status = REQ_STATUS_WAITING_FOR_APPROVAL
            else:
                status = signee_status.status.id
                if signee_status.status.id == REQ_STATUS_NOT_READY:
                    msg = "Not approved!"
                elif signee_status.status.id == REQ_STATUS_READY:
                    if owner_status.status.id == REQ_STATUS_NOT_APPLICABLE:
                        msg = "N/A"
                    else:
                        msg = "OK"
                elif signee_status.status.id == REQ_STATUS_NOT_APPLICABLE:
                    msg = "N/A"
        else:
            status = owner_status.status.id
            if owner_status.status.id == REQ_STATUS_UNKNOWN:
                msg = "?"
            elif owner_status.status.id == REQ_STATUS_NOT_READY:
                msg = "Not ready"

        obj, created = RequirementStatusEntry.objects.get_or_create(
            component_version=self.instance.component_version,
            requirement=self.instance.requirement,
            type=RequirementStatusType.objects.get(pk=REQ_OVERALL_STATUS),
            defaults={
                "status": RequirementStatus.objects.get(pk=status),
                "notes": msg,
            }
        )
        if not created:
            obj.status = RequirementStatus.objects.get(pk=status)
            obj.notes = msg
            obj.save()

        return obj

    def save(self, commit=True, *args, **kwargs):
        if 'requirement' in self.cleaned_data:
            signee_status = None
            owner_status = None

            if 'owner_status' in self.changed_data:  # reset sign off if readiness is changed
                if not self.user.has_perm(SIGNEE_STATUS_PERMISSION):
                    self.cleaned_data['approve_status'] = RequirementStatus.objects.get(pk=REQ_STATUS_UNKNOWN)

            signee_status = self._save_status('approve', REQ_SIGNEE_STATUS)
            owner_status = self._save_status('owner', REQ_OWNER_STATUS)
            return self._save_overall_status(owner_status, signee_status)


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
        qs = super().get_queryset(request)
        # show requirements available for requirement set owners only
        if not request.user.has_perm(OWNER_STATUS_PERMISSION) and \
                request.user.has_perm(SIGNEE_STATUS_PERMISSION):
            return qs.filter(type=REQ_SIGNEE_STATUS,
                             requirement__sets__owner_groups__in=request.user.groups.all()).order_by('requirement_id')
        return qs.filter(type=REQ_OWNER_STATUS).order_by('requirement_id')

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
    search_fields = ('title',)


class RequirementSetAdmin(admin.ModelAdmin):
    filter_horizontal = ['requirements', 'owner_groups']
    list_display = ['name']
    model = RequirementSet
    search_fields = ('name',)


class ComponentAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ['name', 'type', 'data_privacy_class', 'category', 'subcategory', 'vendor']
    model = ComponentModel

    def has_change_permission(self, request, obj=None):
        return request.user.groups.filter(name='Architects').exists() or request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return self.has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_change_permission(request)


@admin.register(FilteredComponent)
class FilteredComponentAdmin(ComponentAdmin):

    def get_form(self, request, obj=None, **kwargs):
        """Override the get_form and extend the 'exclude' keyword arg"""
        if obj:
            kwargs.update({
                'exclude': getattr(kwargs, 'exclude', tuple()) + ('releases',),
            })
        return super(ComponentAdmin, self).get_form(request, obj, **kwargs)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = self.filter_by_version_exists(queryset).filter(name__icontains=search_term)
        return queryset, use_distinct

    @staticmethod
    def filter_by_version_exists(queryset):
        """ Filter component by component version existing. We will hold only component that does not have any
         component version """
        return queryset.filter(component_versions__isnull=True)


class DocTypeAdmin(admin.ModelAdmin):
    pass


class DocLinkFormset(django.forms.models.BaseInlineFormSet):

    def clean(self):
        required_types = []
        types = []
        for form in self.forms:
            try:
                types.append(form.cleaned_data['type'])
            except (AttributeError, KeyError):
                pass
        deleted_types = [f.cleaned_data['type'] for f in self.deleted_forms]
        for dt in deleted_types:
            types.remove(dt)
        required_types = set(required_types) - set(types)
        if required_types:
            error_message = f'You must have {", ".join([t.name for t in required_types])} document type'
            if len(required_types) > 1:
                error_message += 's'
            raise django.forms.ValidationError(error_message)


class DocLinkInline(admin.TabularInline):
    formset = DocLinkFormset
    formfield_overrides = formfields_large
    model = DocLink
    classes = ('collapse', 'no-upper')
    verbose_name = "Document link"
    verbose_name_plural = "Document links"
    extra = 0
    template = 'admin/panopticum/doc_link_edit_inline.html'


class ComponentVersionModelForm(django.forms.ModelForm):
    class Meta:
        model = ComponentVersionModel
        fields = '__all__'
        widgets = {
            'excluded_requirement_set': CheckboxSelectMultiple(),
        }


class ComponentVersionAdmin(admin.ModelAdmin):
    form = ComponentVersionModelForm
    formfield_overrides = formfields_large
    search_fields = ['component__name', 'version']
    list_display = ['component', 'version']
    autocomplete_fields = ['owner_maintainer',
                           'owner_responsible_qa',
                           'owner_product_manager',
                           'owner_program_manager',
                           'owner_expert',
                           'owner_escalation_list',
                           'owner_architect',
                           'component',
                           'dev_language',
                           'dev_framework',
                           'dev_database',
                           'dev_orm',
                           'dev_logging'
                          ]

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
                                     ('dev_raml', 'dev_issuetracker_component'),
                                     ('dev_repo', 'dev_public_repo'),
                                     ('dev_docs', 'dev_public_docs'),
                                     ('dev_build_jenkins_job', 'dev_api_is_public'))}),
        ('Requiremet set', {'classes': ('collapse', 'hidden'), 'fields': ('excluded_requirement_set',)}), # hidden and handled by admin_formset_handlers.js
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
                has_add_permission = inline.has_add_permission(request, obj)
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

    def save_related(self, request, form, formsets, change):
        # save_related() is used to recalculate rating after saving the RequirementStatusEntry
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.update_rating()

    def delete_model(self, request, obj):
        obj.delete_with_dependencies()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete_with_dependencies()

    class Media:
        css = {
                  'all': ('/static/css/admin.css',)
              }


class CredentialsForm(django.forms.ModelForm):
    class Meta:
        model = Credential
        fields = '__all__'
        widgets = {
            'password': django.forms.PasswordInput()
        }


class CredentialsAdmin(admin.ModelAdmin):
    model = Credential
    form = CredentialsForm
    list_display = ('name', 'username', 'description')


class ExternalServiceAdmin(admin.ModelAdmin):
    model = ExternalService
    list_display = ('name', 'link')
    search_fields = ('name',)


class StaticLinksCategoryAdmin(admin.ModelAdmin):
    model = StaticLinksCategoryModel
    search_fields = ('name',)
    list_display = ('name',)


class StaticLinksAdmin(admin.ModelAdmin):
    model = StaticLinksModel
    search_fields = ['name', 'url']
    list_display = ['name', 'url', 'category']
    readonly_fields = ['preview']
    fieldsets = [
        (None, {'fields': ('name', 'url', 'category', 'description')}),
        ('Image', {'fields': (('image', 'preview'),)}),
    ]

    def preview(self, obj):
        max_size = 100
        print(f'\n photo width:  {obj.image.width}\n')
        if obj.image.height < max_size and obj.image.width < max_size:
            max_size = max(obj.image.height, obj.image.width)

        ratio = obj.image.width / obj.image.height
        if obj.image.width >= obj.image.height:
            width = max_size * ratio
            height = max_size
        else:
            height = max_size / ratio
            width = max_size
        return mark_safe(f'<img src="{obj.image.url}" width="{width}" height={height} />')


admin.site.register(User, UserAdmin)
admin.site.register(CountryModel)
admin.site.register(OrganizationModel)
admin.site.register(OrgDepartmentModel)
admin.site.register(PersonRoleModel)

admin.site.register(SoftwareVendorModel)
admin.site.register(DatabaseVendorModel, DatabaseAdmin)
admin.site.register(ProductFamilyModel, ProductFamilyAdmin)
admin.site.register(ProductVersionModel, ProductVersionAdmin)
admin.site.register(ProgrammingLanguageModel, LanguageAdmin)
admin.site.register(FrameworkModel, FrameworkAdmin)
admin.site.register(RuntimeModel, RuntimeAdmin)
admin.site.register(ORMModel, ORMAdmin)
admin.site.register(LoggerModel, LoggerAdmin)
admin.site.register(ComponentType)
admin.site.register(ComponentDataPrivacyClassModel)
admin.site.register(ComponentCategoryModel)
admin.site.register(ComponentSubcategoryModel)
admin.site.register(ComponentModel, ComponentAdmin)
admin.site.register(ComponentVersionModel, ComponentVersionAdmin)
admin.site.register(DeploymentLocationClassModel)
admin.site.register(DeploymentEnvironmentModel)
admin.site.register(TCPPortModel, TCPPortAdmin)
admin.site.register(RequirementSet, RequirementSetAdmin)
admin.site.register(Requirement, RequirementAdmin)
admin.site.register(ExternalService, ExternalServiceAdmin)
admin.site.register(StaticLinksCategoryModel, StaticLinksCategoryAdmin)
admin.site.register(StaticLinksModel, StaticLinksAdmin)

admin.site.register(TechradarInfo)
admin.site.register(TechradarRing)
admin.site.register(TechradarQuadrant)
admin.site.register(TechradarEntry)
