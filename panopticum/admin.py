from django.contrib import admin
from django.forms.widgets import SelectMultiple, NumberInput, TextInput, Select

import datetime

# Register your models here.
from panopticum.models import *


class ComponentVersionAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ForeignKey: {'widget': Select(attrs={'width': '300px', 'style': 'width:300px'})},
                           models.ManyToManyField: {'widget': SelectMultiple(attrs={'size': '7', 'width': '300px', 'style': 'width:300px'})},
                           models.IntegerField: {'widget': NumberInput(attrs={'width': '300px', 'style': 'width:300px'})},
                           models.CharField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})},
                           models.URLField: {'widget': TextInput(attrs={'width': '300px', 'style': 'width:300px'})}
                           }

    fieldsets = (
        (None, {'fields': ('component', 'version', 'comments', 'product', 'depends_on')}),
        ('Ownership', {'classes': ('collapse',),
                       'fields': (
                                  ('owner_maintainer', 'owner_responsible_qa'),
                                  ('owner_product_manager', 'owner_program_manager'),
                                  ('owner_expert', 'owner_escalation_list'), 'owner_architect')}),
        ('Development', {'classes': ('collapse',),
                         'fields': ('dev_life_status', 'dev_language', 'dev_framework', 'dev_database', 'dev_orm', 'dev_logging',
                                    ('dev_raml', 'dev_repo'),
                                    ('dev_documentation', 'dev_jira_component'),
                                    ('dev_build_jenkins_job', 'dev_autotests_report'),
                                    ('dev_api_guideline_compliance', 'dev_api_is_public'))}),
        ('Compliance', {'classes': ('collapse',),
                        'fields': (('compliance_fips', 'compliance_gdpr'),)}),
        ('Operations', {'classes': ('collapse',),
                        'fields': (('op_deployment_name', 'op_binary_name'),
                                   ('op_deployment_type', 'op_open_port'),
                                   ('op_anonymization_support', 'op_metrics'),
                                   ('op_guide_link', 'op_sla_doc_link'),
                                   ('op_capacity_doc_link', 'op_backup_doc_link'),
                                   ('op_horizontal_scalability', 'op_high_availability', 'op_safe_restart',
                                    'op_safe_delete', 'op_safe_redeploy', 'op_zero_downtime_upgrade'))}),
        ('Quality Assurance', {'classes': ('collapse',),
                               'fields': (('qa_manual_tests_quality', 'qa_manual_tests_model', 'qa_manual_tests_link'),
                                          ('qa_unit_tests_quality', 'qa_unit_tests_model', 'qa_unit_tests_link'),
                                          ('qa_e2e_tests_quality', 'qa_e2e_tests_model', 'qa_e2e_tests_link'),
                                          ('qa_perf_tests_quality', 'qa_perf_tests_model', 'qa_perf_tests_link'),
                                          ('qa_security_tests_quality', 'qa_security_tests_model', 'qa_security_tests_link'),
                                          ('qa_longhaul_tests_quality', 'qa_longhaul_tests_model', 'qa_longhaul_tests_link'),
                                          ('qa_api_tests_quality', 'qa_api_tests_model', 'qa_api_tests_link'))}),
    )

    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = ComponentVersionModel.objects.get(id=obj.id)
            if orig_obj.version != obj.version:
                obj.id = None
        obj.meta_update_date = datetime.datetime.now()
        obj.meta_deleted = False
        super().save_model(request, obj, form, change)


admin.site.register(DatacenterModel)

admin.site.register(ComponentRuntimeTypeModel)
admin.site.register(ComponentLocationClassModel)
admin.site.register(ComponentDataPrivacyClassModel)
admin.site.register(ComponentCategoryModel)
admin.site.register(ComponentSubcategoryModel)

admin.site.register(SoftwareVendorModel)
admin.site.register(DatabaseVendorModel)
admin.site.register(DeploymentTypeModel)
admin.site.register(ProductFamilyModel)
admin.site.register(ProductModel)
admin.site.register(ProgrammingLanguageModel)
admin.site.register(FrameworkModel)
admin.site.register(ORMModel)
admin.site.register(OSFamilyModel)
admin.site.register(LoggerModel)
admin.site.register(TCPPortModel)
admin.site.register(TestingModel)

admin.site.register(PersonRoleModel)
admin.site.register(PersonModel)

admin.site.register(ComponentModel)
admin.site.register(ComponentVersionModel, ComponentVersionAdmin)
