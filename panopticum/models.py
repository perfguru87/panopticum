from django.db import models
from datatableview.views import DatatableView
from datatableview import helpers
from django.forms.models import model_to_dict


##################################################################################################
# People, Org chart
##################################################################################################


class CountryModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class OrgDepartmentModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class OrganizationModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class PersonRoleModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class PersonModel(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    title = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField()
    organization = models.ForeignKey(OrganizationModel, on_delete=models.PROTECT, blank=True, null=True)
    org_department = models.ForeignKey(OrgDepartmentModel, on_delete=models.PROTECT, blank=True, null=True)
    country = models.ForeignKey(CountryModel, on_delete=models.PROTECT, blank=True, null=True)
    office_phone = models.CharField(max_length=64, blank=True, null=True)
    mobile_phone = models.CharField(max_length=64, blank=True, null=True)
    active_directory_guid = models.CharField(max_length=64, blank=True, null=True)
    employee_number = models.CharField(max_length=64, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    role = models.ForeignKey(PersonRoleModel, on_delete=models.PROTECT, blank=True, null=True)
    manager = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)
    hidden = models.BooleanField(help_text="Hide the person from the potential assignee lists", db_index=True, default=False)

    class Meta:
        ordering = ['email']

    def __str__(self):
        return self.email


##################################################################################################
# Components
##################################################################################################


LIFE_STATUS = (
    ('unknown', "?"),
    ('new', "New"),
    ('mature', "Mature"),
    ('legacy', "Legacy"),
    ('eol', "End Of Life"),
    ('eos', "End Of Support"),
)


LOW_MED_HIGH = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('none', "None"),
    ('low', "Low"),
    ('med', "Med"),
    ('high', "High")
)


LOW_MED_HIGH_RATING = {'unknown': 0, 'n/a': 3, 'none': 0, 'low': 1, 'med': 2, 'high': 3}


NO_PARTIAL_YES = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('no', "No"),
    ('partial', "Partial"),
    ('yes', "Yes")
)


NO_PARTIAL_YES_RATING = {'unknown': 0, 'n/a': 2, 'no': 0, 'partial': 1, 'yes': 2}


DEPENDENCY_TYPE = (
    ('sync_rw', "Sync R/W"),
    ('sync_ro', "Sync R/O"),
    ('sync_wo', "Sync W/O"),
    ('async_rw', "Async R/W"),
    ('async_ro', "Async R/O"),
    ('async_wo', "Async W/O"),
)


class NoPartialYesField(models.CharField):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['max_length'] = 16
        kwargs['choices'] = NO_PARTIAL_YES
        kwargs['default'] = kwargs['choices'][0][0]
        super().__init__(*args, **kwargs)


class LowMedHighField(models.CharField):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['max_length'] = 16
        kwargs['choices'] = LOW_MED_HIGH
        kwargs['default'] = kwargs['choices'][0][0]
        super().__init__(*args, **kwargs)


class URLsField(models.CharField):
    def __init__(self, _title="", *args, **kwargs):
        # FIXME: store array of URLs (e.g. "|"-separated)
        kwargs['verbose_name'] = _title
        kwargs['max_length'] = 2048
        kwargs['default'] = ""
        super().__init__(*args, **kwargs)


class MarkupField(models.TextField):
    # FIXME: store arbitrary comments and replace JIRA items and URLs by links
    def __init__(self, _title="", *args, **kwargs):
        # FIXME: store array of URLs (e.g. "|"-separated)
        kwargs['verbose_name'] = _title
        kwargs['default'] = ""
        kwargs['blank'] = True
        super().__init__(*args, **kwargs)


class SigneeField(models.ForeignKey):
    def __init__(self, _title="", *args, **kwargs):
        kwargs['verbose_name'] = _title
        kwargs['on_delete'] = on_delete=models.PROTECT
        kwargs['null'] = True
        kwargs['blank'] = True
        kwargs['to'] = 'panopticum.PersonModel'
        super().__init__(*args, **kwargs)


class ComponentDataPrivacyClassModel(models.Model):
    name = models.CharField(max_length=64,
                            help_text="Data Access, Secrets Management, Sensitive Metadata, Non-sensitive Metadata")
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentCategoryModel(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentSubcategoryModel(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class SoftwareVendorModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component vendor: OpenSource, MyCompany, ...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class DatabaseVendorModel(models.Model):
    name = models.CharField(max_length=64, help_text="Database vendor: MSSQl, Oracle, SQLite, PostgreSQL, MySQL, Percona")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ProgrammingLanguageModel(models.Model):
    name = models.CharField(max_length=64, help_text="Programming language")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class FrameworkModel(models.Model):
    name = models.CharField(max_length=64, help_text="Framework")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ORMModel(models.Model):
    name = models.CharField(max_length=64, help_text="ORM")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class LoggerModel(models.Model):
    name = models.CharField(max_length=64, help_text="Logger model")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentRuntimeTypeModel(models.Model):
    name = models.CharField(max_length=64, help_text="Library, Framework, Driver, OS Service, OS Process, Web Service, Database, MQ")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component short name")
    description = models.TextField(blank=True, null=True)

    life_status = models.CharField(max_length=16, choices=LIFE_STATUS, default=LIFE_STATUS[0][0])
    runtime_type = models.ForeignKey(ComponentRuntimeTypeModel, on_delete=models.PROTECT)
    data_privacy_class = models.ForeignKey(ComponentDataPrivacyClassModel, on_delete=models.PROTECT)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(ComponentSubcategoryModel, blank=True, null=True, on_delete=models.PROTECT)

    vendor = models.ForeignKey(SoftwareVendorModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentVersionModel(models.Model):
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, null=True)

    # dependencies

    depends_on = models.ManyToManyField(ComponentModel, related_name='dependee', through='ComponentDependencyModel')

    # deployment capabilities

    locations = models.ManyToManyField('DeploymentLocationClassModel', related_name='component_versions', blank=True)

    # ownership

    owner_maintainer = models.ForeignKey(PersonModel, related_name='maintainer_of', on_delete=models.PROTECT, blank=True, null=True)
    owner_responsible_qa = models.ForeignKey(PersonModel, related_name='responsible_qa_of',
                                             on_delete=models.PROTECT, blank=True, null=True)
    owner_product_manager = models.ManyToManyField(PersonModel, related_name='product_manager_of', blank=True)
    owner_program_manager = models.ManyToManyField(PersonModel, related_name='program_managed_of', blank=True)
    owner_escalation_list = models.ManyToManyField(PersonModel, related_name='escalation_list_of', blank=True)
    owner_expert = models.ManyToManyField(PersonModel, related_name='expert_of', blank=True)
    owner_architect = models.ManyToManyField(PersonModel, related_name='architect_of', blank=True)

    # development

    dev_language = models.ManyToManyField(ProgrammingLanguageModel, blank=True)
    dev_framework = models.ManyToManyField(FrameworkModel, blank=True)
    dev_database = models.ManyToManyField(DatabaseVendorModel, blank=True)
    dev_orm = models.ManyToManyField(ORMModel, blank=True)
    dev_logging = models.ManyToManyField(LoggerModel, blank=True)

    dev_raml = URLsField("RAML link", blank=True, null=True)
    dev_repo = URLsField("Repository", blank=True, null=True)
    dev_public_repo = URLsField("Repository", blank=True, null=True)
    dev_jira_component = URLsField("JIRA component", blank=True, null=True)
    dev_build_jenkins_job = URLsField("Jenkins job to build the component", blank=True, null=True)
    dev_docs = URLsField("Documentation entry page", blank=True, null=True)
    dev_public_docs = URLsField("Documentation entry page", blank=True, null=True)
    dev_commit_link = URLsField("Commit link", blank=True, null=True)

    dev_api_is_public = NoPartialYesField("API is public")

    # compliance

    compliance_applicable = models.BooleanField(help_text="Compliance requirements applicable?", default=True)

    compliance_fips_status = NoPartialYesField("FIPS compliance")
    compliance_fips_notes = MarkupField("FIPS compliance notes")
    compliance_fips_signoff = SigneeField(related_name='signed_fips')

    compliance_gdpr_status = NoPartialYesField("GDPR compliance")
    compliance_gdpr_notes = MarkupField("GDRP compliance notes")
    compliance_gdpr_signoff = SigneeField(related_name='signed_gdpr')

    compliance_api_status = NoPartialYesField("API guildeine compliance")
    compliance_api_notes = MarkupField("API guideline compliance notes")
    compliance_api_signoff = SigneeField(related_name='signed_api_guideline')

    # operational readiness information

    op_applicable = models.BooleanField(help_text="Operational requirements applicable?", default=True)

    op_guide_status = NoPartialYesField("Operations guide")
    op_guide_notes = MarkupField("Operations guide notes")
    op_guide_signoff = SigneeField(related_name='signed_op_guide')

    op_failover_status = NoPartialYesField("Failover")
    op_failover_notes = MarkupField("Failover notes")
    op_failover_signoff = SigneeField(related_name='signed_failover')

    op_horizontal_scalability_status = NoPartialYesField("Horizontal scalability")
    op_horizontal_scalability_notes = MarkupField("Horizontal scalability notes")
    op_horizontal_scalability_signoff = SigneeField(related_name='signed_horizontal_scalability')

    op_scaling_guide_status = NoPartialYesField("Scaling guide")
    op_scaling_guide_notes = MarkupField("Scaling guide notes")
    op_scaling_guide_signoff = SigneeField(related_name='signed_scaling_guide')

    op_sla_guide_status = NoPartialYesField("SLA/SLO guide")
    op_sla_guide_notes = MarkupField("SLA/SLO guide")
    op_sla_guide_signoff = SigneeField(related_name='signed_sla_guide')

    op_metrics_status = NoPartialYesField("Monitoring")
    op_metrics_notes = MarkupField("Monitoring notes")
    op_metrics_signoff = SigneeField(related_name='signed_metrics')

    op_alerts_status = NoPartialYesField("Alerts guide")
    op_alerts_notes = MarkupField("Alerts guide notes")
    op_alerts_signoff = SigneeField(related_name='signed_alerts')

    op_zero_downtime_status = NoPartialYesField("Zero-downtime upgrade")
    op_zero_downtime_notes = MarkupField("Zero-downtime upgrade notes")
    op_zero_downtime_signoff = SigneeField(related_name='signed_zero_downtime')

    op_backup_status = NoPartialYesField("Backup")
    op_backup_notes = MarkupField("Backup notes")
    op_backup_signoff = SigneeField(related_name='signed_backup')

    op_safe_restart = models.BooleanField(help_text="Is it safe to restart?", blank=True, null=True)
    op_safe_delete = models.BooleanField(help_text="Is it safe to delete?", blank=True, null=True)
    op_safe_redeploy = models.BooleanField(help_text="Is it safe to redeploy?", blank=True, null=True)

    # maintainability

    mt_applicable = models.BooleanField(help_text="Maintainability requirements applicable?", default=True)

    mt_http_tracing_status = NoPartialYesField("HTTP requests tracing", help_text="HTTP request b3 propagation support")
    mt_http_tracing_notes = MarkupField("HTTP requests tracing notes")
    mt_http_tracing_signoff = SigneeField(related_name='signed_http_tracing')

    mt_logging_completeness_status = NoPartialYesField("Logging completeness", help_text="Are logs sufficient?")
    mt_logging_completeness_notes = MarkupField("Logging completeness notes")
    mt_logging_completeness_signoff = SigneeField(related_name='signed_logging_completeness')

    mt_logging_format_status = NoPartialYesField("Logging format")
    mt_logging_format_notes = MarkupField("Logging format notes")
    mt_logging_format_signoff = SigneeField(related_name='signed_logging_format')

    mt_logging_storage_status = NoPartialYesField("Logging storage", help_text="Is proper logs storage used?")
    mt_logging_storage_notes = MarkupField("Logging storage notes")
    mt_logging_storage_signoff = SigneeField(related_name='signed_logging_storage')

    mt_logging_sanitization_status = NoPartialYesField("Logging sanitization")
    mt_logging_sanitization_notes = MarkupField("Logging sanitization notes")
    mt_logging_sanitization_signoff = SigneeField(related_name='signed_logggin_sanitization')

    mt_db_anonymisation_status = NoPartialYesField("DataBase anonymisation")
    mt_db_anonymisation_notes = MarkupField("DataBase anonymisation")
    mt_db_anonymisation_signoff = SigneeField(related_name='signed_db_anonymisation')

    # quality assurance

    qa_applicable = models.BooleanField(help_text="Tests requirements applicable?", default=True)

    qa_manual_tests_quality = LowMedHighField("Manual tests")
    qa_manual_tests_notes = MarkupField("Manual tests notes")
    qa_manual_tests_signoff = SigneeField(related_name='signed_manual_tests')

    qa_unit_tests_quality = LowMedHighField("Unit tests")
    qa_unit_tests_notes = MarkupField("Unit tests notes")
    qa_unit_tests_signoff = SigneeField(related_name='signed_unit_tests')

    qa_e2e_tests_quality = LowMedHighField("E2E tests")
    qa_e2e_tests_notes = MarkupField("E2E tests notes")
    qa_e2e_tests_signoff = SigneeField(related_name='signed_e2e_tests')

    qa_perf_tests_quality = LowMedHighField("Performance tests")
    qa_perf_tests_notes = MarkupField("Perf tests notes")
    qa_perf_tests_signoff = SigneeField(related_name='signed_perf_tests')

    qa_longhaul_tests_quality = LowMedHighField("Long-haul tests")
    qa_longhaul_tests_notes = MarkupField("Long-hault tests notes")
    qa_longhaul_tests_signoff = SigneeField(related_name='signed_longhaul_tests')

    qa_security_tests_quality = LowMedHighField("Security tests")
    qa_security_tests_notes = MarkupField("Security tests notes")
    qa_security_tests_signoff = SigneeField(related_name='signed_security_tests')

    qa_api_tests_quality = LowMedHighField("API tests")
    qa_api_tests_notes = MarkupField("API tests notes")
    qa_api_tests_signoff = SigneeField(related_name='signed_api_tests')

    # meta

    meta_update_by = models.ForeignKey(PersonModel, on_delete=models.PROTECT, blank=True, null=True, related_name='updater_of')
    meta_update_date = models.DateTimeField()
    meta_deleted = models.BooleanField()

    meta_compliance_rating = models.IntegerField(default=0)
    meta_mt_rating = models.IntegerField(default=0)
    meta_op_rating = models.IntegerField(default=0)
    meta_qa_rating = models.IntegerField(default=0)
    meta_rating = models.IntegerField(default=0)
    meta_profile_completeness = models.IntegerField(default=0)
    meta_profile_not_filled_fields = models.TextField(default="")
    meta_bad_rating_fields = models.TextField(default="")

    def _update_any_rating(self, target, condition, dictionary, fields):
        rating = 0
        max_rating = 0
        bad_rating = []

        if self.__dict__[condition]:
            m = max(dictionary.values())
            for f in fields:
                r = dictionary.get(self.__dict__[f], 0)
                rating += r
                max_rating += m
                if r != m:
                    bad_rating.append("%s=%s" % (f, self.__dict__[f]))
        else:
            rating = 1
            max_rating = 1

        self.__dict__[target] = int(100 * rating / max_rating)
        return rating, max_rating, bad_rating

    def _update_compliance_rating(self):
        return self._update_any_rating('meta_compliance_rating', 'compliance_applicable', NO_PARTIAL_YES_RATING,
                                       ('compliance_fips_status', 'compliance_gdpr_status',
                                        'compliance_api_status'))

    def _update_mt_rating(self):
        return self._update_any_rating('meta_mt_rating', 'mt_applicable', NO_PARTIAL_YES_RATING,
                                       ('mt_http_tracing_status', 'mt_logging_completeness_status',
                                        'mt_logging_format_status', 'mt_logging_storage_status',
                                        'mt_logging_sanitization_status', 'mt_db_anonymisation_status'))

    def _update_op_rating(self):
        return self._update_any_rating('meta_op_rating', 'op_applicable', NO_PARTIAL_YES_RATING,
                                       ('op_guide_status', 'op_failover_status',
                                        'op_horizontal_scalability_status', 'op_scaling_guide_status',
                                        'op_sla_guide_status', 'op_metrics_status',
                                        'op_alerts_status', 'op_zero_downtime_status',
                                        'op_backup_status'))

    def _update_qa_rating(self):
        return self._update_any_rating('meta_qa_rating', 'qa_applicable', LOW_MED_HIGH_RATING,
                                       ('qa_manual_tests_quality', 'qa_unit_tests_quality',
                                        'qa_e2e_tests_quality', 'qa_perf_tests_quality',
                                        'qa_longhaul_tests_quality', 'qa_security_tests_quality',
                                        'qa_api_tests_quality'))

    def _get_profile_must_fields(self):
        ret = ['owner_maintainer', 'owner_responsible_qa', 'owner_product_manager', 'owner_program_manager',
                'owner_escalation_list', 'owner_expert', 'owner_architect',
                'dev_language', 'dev_raml', 'dev_repo', 'dev_jira_component', 'dev_docs', 'dev_api_is_public',
                'compliance_fips_status', 'compliance_gdpr_status', 'compliance_api_status']

        if self.compliance_applicable:
            ret += ['compliance_fips_status', 'compliance_gdpr_status', 'compliance_api_status']

        if self.op_applicable:
            ret += ['op_guide_status', 'op_failover_status', 'op_horizontal_scalability_status',
                    'op_scaling_guide_status', 'op_sla_guide_status', 'op_metrics_status', 'op_alerts_status',
                    'op_zero_downtime_status', 'op_backup_status', 'op_safe_restart']

        if self.mt_applicable:
            ret += ['mt_http_tracing_status', 'mt_logging_completeness_status', 'mt_logging_format_status',
                    'mt_logging_storage_status', 'mt_logging_sanitization_status', 'mt_db_anonymisation_status']

        if self.qa_applicable:
            ret += ['qa_manual_tests_quality', 'qa_unit_tests_quality', 'qa_e2e_tests_quality',
                    'qa_perf_tests_quality', 'qa_longhaul_tests_quality', 'qa_security_tests_quality',
                    'qa_api_tests_quality']

        return ret

    def _field_is_filled(self, field):
        d = model_to_dict(self)
        return 0 if d[field] in ("unknown", "", None, "?") else 1

    def _update_profile_completeness(self):
        completeness = 0
        max_completeness = 0
        not_filled_fields = set()

        for f in self._get_profile_must_fields():
            if self._field_is_filled(f):
                completeness += 1
            else:
                not_filled_fields.add(f)
            max_completeness += 1

        self.meta_profile_completeness = int(100 * completeness / max_completeness)
        self.meta_profile_not_filled_fields = ", ".join(sorted(not_filled_fields))

    def _update_rating(self):
        rating = 0
        max_rating = 0
        bad_rating = []

        for f in (self._update_mt_rating, self._update_op_rating, self._update_qa_rating):
            r, mr, br = f()
            rating += r
            max_rating += mr
            bad_rating += br

        self.meta_rating = int(100 * rating / max_rating)
        self.meta_bad_rating_fields = ", ".join(bad_rating)

    def save(self, *args, **kwargs):
        self._update_profile_completeness()
        self._update_rating()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return "#%d %s - %s" % (self.id, self.component.name, self.version)


class ComponentDependencyModel(models.Model):
    type = models.CharField(max_length=16, choices=DEPENDENCY_TYPE, default=DEPENDENCY_TYPE[0][0])
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT)
    version = models.ForeignKey(ComponentVersionModel, on_delete=models.PROTECT)


##################################################################################################
# Deployments, products, etc
##################################################################################################

class DeploymentLocationClassModel(models.Model):
    name = models.CharField(max_length=64, help_text="global, per-datacenter, customer, endpoint")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class DeploymentEnvironmentModel(models.Model):
    name = models.CharField(max_length=64, help_text="K8S, Windows VM, Linux VM,...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TCPPortModel(models.Model):
    name = models.CharField(max_length=64, help_text="TCP/IP port name: HTTP, SSH, ...")
    port = models.IntegerField(help_text="TCP/IP port: 80, 21, ...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentDeploymentModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component deployment type: Cloud Account Server")
    location_class = models.ManyToManyField(DeploymentLocationClassModel)
    environment = models.ForeignKey(DeploymentEnvironmentModel, on_delete=models.PROTECT)
    component_version = models.ForeignKey(ComponentVersionModel, on_delete=models.PROTECT)
    service_name = models.CharField(max_length=64, help_text="accsrv, taskmngr", blank=True)
    binary_name = models.CharField(max_length=64, help_text="accsrv.exe", blank=True)
    open_ports = models.ManyToManyField(TCPPortModel)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ProductFamilyModel(models.Model):
    name = models.CharField(max_length=64, help_text="Product family")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ProductModel(models.Model):
    name = models.CharField(max_length=64, help_text="Product")
    family = models.ForeignKey(ProductFamilyModel, on_delete=models.PROTECT)
    order = models.IntegerField(help_text="sorting order")
    components_deployments = models.ManyToManyField(ComponentDeploymentModel)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class DatacenterModel(models.Model):
    name = models.CharField(max_length=64, help_text="Datacenter name")
    info = URLsField("Info link", blank=True, null=True)
    grafana = URLsField("Grafana link", blank=True, null=True)
    metrics = URLsField("Metrics link", blank=True, null=True)
    components_deployments = models.ManyToManyField(ComponentDeploymentModel)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)
