from django.db import models
from panopticum import fields
from django.forms.models import model_to_dict
import datetime


##################################################################################################
# People, Org chart
##################################################################################################


class Country(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Department(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Organization(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class PersonRole(models.Model):
    name = models.CharField(max_length=64, default="")


    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Person(models.Model):
    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    title = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField()
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT, blank=True, null=True)
    org_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, blank=True, null=True)
    office_phone = models.CharField(max_length=64, blank=True, null=True)
    mobile_phone = models.CharField(max_length=64, blank=True, null=True)
    active_directory_guid = models.CharField(max_length=64, blank=True, null=True)
    employee_number = models.CharField(max_length=64, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT, blank=True, null=True)
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


LOW_MED_HIGH_RATING = {'unknown': 0, 'n/a': 3, 'none': 0, 'low': 1, 'med': 2, 'high': 3}


NO_PARTIAL_YES_RATING = {'unknown': 0, 'n/a': 2, 'no': 0, 'partial': 1, 'yes': 2}


DEPENDENCY_TYPE = (
    ('sync_rw', "Sync R/W"),
    ('sync_ro', "Sync R/O"),
    ('sync_wo', "Sync W/O"),
    ('async_rw', "Async R/W"),
    ('async_ro', "Async R/O"),
    ('async_wo', "Async W/O"),
    ('includes', "Includes")
)


class ComponentDataPrivacyClass(models.Model):
    name = models.CharField(max_length=64,
                            help_text="Data Access, Secrets Management, Sensitive Metadata, Non-sensitive Metadata")
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentCategory(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)

class ComponentSubcategory(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ComponentCategory, on_delete=models.PROTECT)

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class SoftwareVendor(models.Model):
    name = models.CharField(max_length=64, help_text="Component vendor: OpenSource, MyCompany, ...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class DatabaseVendor(models.Model):
    name = models.CharField(max_length=64, help_text="Database vendor: MSSQl, Oracle, SQLite, PostgreSQL, MySQL, Percona")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ProgrammingLanguage(models.Model):
    name = models.CharField(max_length=64, help_text="Programming language")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Framework(models.Model):
    name = models.CharField(max_length=64, help_text="Framework")
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.PROTECT)

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ORM(models.Model):
    name = models.CharField(max_length=64, help_text="ORM")
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.PROTECT)

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Logger(models.Model):
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


class ComponentRuntimeType(models.Model):
    name = models.CharField(max_length=64,
                            help_text="Library, Framework, Driver, OS Service, OS Process, Web Service, Database, MQ")


class Component(models.Model):
    name = models.CharField(max_length=64, help_text="Component short name")
    description = models.TextField(blank=True, null=True)

    life_status = models.CharField(max_length=16, choices=LIFE_STATUS, default=LIFE_STATUS[0][0])
    runtime_type = models.ForeignKey(ComponentRuntimeType, on_delete=models.PROTECT)
    data_privacy_class = models.ForeignKey(ComponentDataPrivacyClass, on_delete=models.PROTECT)
    category = models.ForeignKey(ComponentCategory, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(ComponentSubcategory, blank=True, null=True, on_delete=models.PROTECT)
    vendor = models.ForeignKey(SoftwareVendor, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentVersion(models.Model):
    component = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, verbose_name="Version or build",
                               help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, null=True)

    # dependencies

    depends_on = models.ManyToManyField(Component, related_name='dependee', through='ComponentDependency')

    # deployment capabilities

    locations = models.ManyToManyField('DeploymentLocationClass', help_text='possible component deployment locations',
                                       related_name='component_versions', blank=True)

    # ownership

    owner_maintainer = models.ForeignKey(Person, related_name='maintainer_of', on_delete=models.PROTECT, blank=True, null=True)
    owner_responsible_qa = models.ForeignKey(Person, related_name='responsible_qa_of',
                                             on_delete=models.PROTECT, blank=True, null=True)
    owner_product_manager = models.ManyToManyField(Person, related_name='product_manager_of', blank=True)
    owner_program_manager = models.ManyToManyField(Person, related_name='program_managed_of', blank=True)
    owner_escalation_list = models.ManyToManyField(Person, related_name='escalation_list_of', blank=True)
    owner_expert = models.ManyToManyField(Person, related_name='expert_of', blank=True)
    owner_architect = models.ManyToManyField(Person, related_name='architect_of', blank=True)

    # development

    dev_language = models.ManyToManyField(ProgrammingLanguage, verbose_name="Language", blank=True)
    dev_framework = models.ManyToManyField(Framework, verbose_name="Frameworks", blank=True)
    dev_database = models.ManyToManyField(DatabaseVendor, verbose_name="Supported Databases", blank=True)
    dev_orm = models.ManyToManyField(ORM, verbose_name="ORM", blank=True)
    dev_logging = models.ManyToManyField(Logger, verbose_name="Logging framework", blank=True)

    dev_raml = fields.SmartTextField("RAML link", help_text="Multiple links allowed")
    dev_repo = fields.SmartTextField("Repository", help_text="Multiple links allowed")
    dev_public_repo = fields.SmartTextField("Public Repository", help_text="Multiple links allowed")
    dev_jira_component = fields.SmartTextField("JIRA component", help_text="Multiple links allowed")
    dev_build_jenkins_job = fields.SmartTextField("Jenkins job to build the component", help_text="Multiple links allowed")
    dev_docs = fields.SmartTextField("Documentation entry page", help_text="Multiple links allowed")
    dev_public_docs = fields.SmartTextField("Public Documentation", help_text="Multiple links allowed")
    dev_commit_link = fields.SmartTextField("Commit link", help_text="Multiple links allowed")

    dev_api_is_public = fields.NoPartialYesField("API is public")

    # compliance

    compliance_applicable = models.BooleanField(verbose_name="Compliance requirements are applicable", default=True)

    compliance_fips_status = fields.NoPartialYesField("FIPS compliance")
    compliance_fips_notes = fields.SmartTextField("FIPS compliance notes")
    compliance_fips_signoff = fields.SigneeField(related_name='signed_fips')

    compliance_gdpr_status = fields.NoPartialYesField("GDPR compliance")
    compliance_gdpr_notes = fields.SmartTextField("GDRP compliance notes")
    compliance_gdpr_signoff = fields.SigneeField(related_name='signed_gdpr')

    compliance_api_status = fields.NoPartialYesField("API guildeine compliance")
    compliance_api_notes = fields.SmartTextField("API guideline compliance notes")
    compliance_api_signoff = fields.SigneeField(related_name='signed_api_guideline')

    # operational readiness information

    op_applicable = models.BooleanField(verbose_name="Operational requirements are applicable", default=True)

    op_guide_status = fields.NoPartialYesField("Operations guide")
    op_guide_notes = fields.SmartTextField("Operations guide notes")
    op_guide_signoff = fields.SigneeField(related_name='signed_op_guide')

    op_failover_status = fields.NoPartialYesField("Failover")
    op_failover_notes = fields.SmartTextField("Failover notes")
    op_failover_signoff = fields.SigneeField(related_name='signed_failover')

    op_horizontal_scalability_status = fields.NoPartialYesField("Horizontal scalability")
    op_horizontal_scalability_notes = fields.SmartTextField("Horizontal scalability notes")
    op_horizontal_scalability_signoff = fields.SigneeField(related_name='signed_horizontal_scalability')

    op_scaling_guide_status = fields.NoPartialYesField("Scaling guide")
    op_scaling_guide_notes = fields.SmartTextField("Scaling guide notes")
    op_scaling_guide_signoff = fields.SigneeField(related_name='signed_scaling_guide')

    op_sla_guide_status = fields.NoPartialYesField("SLA/SLO guide")
    op_sla_guide_notes = fields.SmartTextField("SLA/SLO guide notes")
    op_sla_guide_signoff = fields.SigneeField(related_name='signed_sla_guide')

    op_metrics_status = fields.NoPartialYesField("Monitoring")
    op_metrics_notes = fields.SmartTextField("Monitoring notes")
    op_metrics_signoff = fields.SigneeField(related_name='signed_metrics')

    op_alerts_status = fields.NoPartialYesField("Alerts guide")
    op_alerts_notes = fields.SmartTextField("Alerts guide notes")
    op_alerts_signoff = fields.SigneeField(related_name='signed_alerts')

    op_zero_downtime_status = fields.NoPartialYesField("Zero-downtime upgrade")
    op_zero_downtime_notes = fields.SmartTextField("Zero-downtime upgrade notes")
    op_zero_downtime_signoff = fields.SigneeField(related_name='signed_zero_downtime')

    op_backup_status = fields.NoPartialYesField("Backup")
    op_backup_notes = fields.SmartTextField("Backup notes")
    op_backup_signoff = fields.SigneeField(related_name='signed_backup')

    op_safe_restart = models.BooleanField(help_text="Is it safe to restart?", blank=True, null=True)
    op_safe_delete = models.BooleanField(help_text="Is it safe to delete?", blank=True, null=True)
    op_safe_redeploy = models.BooleanField(help_text="Is it safe to redeploy?", blank=True, null=True)

    # maintainability

    mt_applicable = models.BooleanField(verbose_name="Maintainability requirements are applicable", default=True)

    mt_http_tracing_status = fields.NoPartialYesField("HTTP requests tracing",
                                                      help_text="HTTP request b3 propagation support")
    mt_http_tracing_notes = fields.SmartTextField("HTTP requests tracing notes")
    mt_http_tracing_signoff = fields.SigneeField(related_name='signed_http_tracing')

    mt_logging_completeness_status = fields.NoPartialYesField("Logging completeness",
                                                              help_text="Are logs sufficient?")
    mt_logging_completeness_notes = fields.SmartTextField("Logging completeness notes")
    mt_logging_completeness_signoff = fields.SigneeField(related_name='signed_logging_completeness')

    mt_logging_format_status = fields.NoPartialYesField("Logging format", help_text="Logs have proper format")
    mt_logging_format_notes = fields.SmartTextField("Logging format notes")
    mt_logging_format_signoff = fields.SigneeField(related_name='signed_logging_format')

    mt_logging_storage_status = fields.NoPartialYesField("Logging storage", help_text="Is proper logs storage used?")
    mt_logging_storage_notes = fields.SmartTextField("Logging storage notes")
    mt_logging_storage_signoff = fields.SigneeField(related_name='signed_logging_storage')

    mt_logging_sanitization_status = fields.NoPartialYesField("Logs sanitization",
                                                              help_text="Logs do not have sensitive information")
    mt_logging_sanitization_notes = fields.SmartTextField("Logging sanitization notes")
    mt_logging_sanitization_signoff = fields.SigneeField(related_name='signed_logggin_sanitization')

    mt_db_anonymisation_status = fields.NoPartialYesField("DataBase anonymisation")
    mt_db_anonymisation_notes = fields.SmartTextField("DataBase anonymisation")
    mt_db_anonymisation_signoff = fields.SigneeField(related_name='signed_db_anonymisation')

    # quality assurance

    qa_applicable = models.BooleanField(verbose_name="Tests requirements are applicable", default=True)

    qa_manual_tests_status = fields.LowMedHighField("Manual tests", help_text="Completeness, coverage, quality")
    qa_manual_tests_notes = fields.SmartTextField("Manual tests notes")
    qa_manual_tests_signoff = fields.SigneeField(related_name='signed_manual_tests')

    qa_unit_tests_status = fields.LowMedHighField("Unit tests", help_text="Completeness, coverage, quality")
    qa_unit_tests_notes = fields.SmartTextField("Unit tests notes")
    qa_unit_tests_signoff = fields.SigneeField(related_name='signed_unit_tests')

    qa_e2e_tests_status = fields.LowMedHighField("E2E tests", help_text="Completeness, coverage, quality")
    qa_e2e_tests_notes = fields.SmartTextField("E2E tests notes")
    qa_e2e_tests_signoff = fields.SigneeField(related_name='signed_e2e_tests')

    qa_perf_tests_status = fields.LowMedHighField("Performance tests", help_text="Completeness, coverage, quality")
    qa_perf_tests_notes = fields.SmartTextField("Perf tests notes")
    qa_perf_tests_signoff = fields.SigneeField(related_name='signed_perf_tests')

    qa_longhaul_tests_status = fields.LowMedHighField("Long-haul tests", help_text="Completeness, coverage, quality")
    qa_longhaul_tests_notes = fields.SmartTextField("Long-hault tests notes")
    qa_longhaul_tests_signoff = fields.SigneeField(related_name='signed_longhaul_tests')

    qa_security_tests_status = fields.LowMedHighField("Security tests", help_text="Completeness, coverage, quality")
    qa_security_tests_notes = fields.SmartTextField("Security tests notes")
    qa_security_tests_signoff = fields.SigneeField(related_name='signed_security_tests')

    qa_api_tests_status = fields.LowMedHighField("API tests", help_text="Completeness, coverage, quality")
    qa_api_tests_notes = fields.SmartTextField("API tests notes")
    qa_api_tests_signoff = fields.SigneeField(related_name='signed_api_tests')

    qa_anonymisation_tests_status = fields.LowMedHighField("DB anonymisation tests")
    qa_anonymisation_tests_notes = fields.SmartTextField("DB anonymisation tests notes")
    qa_anonymisation_tests_signoff = fields.SigneeField(related_name='signed_anonymisation_tests')

    qa_upgrade_tests_status = fields.LowMedHighField("Upgrade tests", help_text="Functional, performance, real volume")
    qa_upgrade_tests_notes = fields.SmartTextField("Upgrade tests notes")
    qa_upgrade_tests_signoff = fields.SigneeField(related_name='signed_upgrade_tests')

    # meta

    meta_update_by = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True, related_name='updater_of')
    meta_update_date = models.DateTimeField(db_index=True)
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

    @staticmethod
    def get_compliance_fields():
        return ('compliance_fips_status', 'compliance_gdpr_status', 'compliance_api_status')

    @staticmethod
    def get_operations_fields():
        return ('op_guide_status', 'op_failover_status', 'op_horizontal_scalability_status', 'op_scaling_guide_status',
                'op_sla_guide_status', 'op_metrics_status', 'op_alerts_status', 'op_zero_downtime_status', 'op_backup_status')

    @staticmethod
    def get_maintenance_fields():
        return ('mt_http_tracing_status', 'mt_logging_completeness_status', 'mt_logging_format_status',
                'mt_logging_storage_status', 'mt_logging_sanitization_status', 'mt_db_anonymisation_status')

    @staticmethod
    def get_quality_assurance_fields():
        return ('qa_manual_tests_status', 'qa_unit_tests_status', 'qa_e2e_tests_status', 'qa_perf_tests_status',
                'qa_longhaul_tests_status', 'qa_security_tests_status', 'qa_api_tests_status',
                'qa_anonymisation_tests_status', 'qa_upgrade_tests_status')

    def _update_compliance_rating(self):
        return self._update_any_rating('meta_compliance_rating', 'compliance_applicable', NO_PARTIAL_YES_RATING,
                                       ComponentVersion.get_compliance_fields())

    def _update_mt_rating(self):
        return self._update_any_rating('meta_mt_rating', 'mt_applicable', NO_PARTIAL_YES_RATING,
                                       ComponentVersion.get_maintenance_fields())

    def _update_op_rating(self):
        return self._update_any_rating('meta_op_rating', 'op_applicable', NO_PARTIAL_YES_RATING,
                                       ComponentVersion.get_operations_fields())

    def _update_qa_rating(self):
        return self._update_any_rating('meta_qa_rating', 'qa_applicable', LOW_MED_HIGH_RATING,
                                       ComponentVersion.get_quality_assurance_fields())

    def _get_profile_must_fields(self):
        ret = ['owner_maintainer', 'owner_responsible_qa', 'owner_product_manager', 'owner_program_manager',
                'owner_escalation_list', 'owner_expert', 'owner_architect',
                'dev_language', 'dev_raml', 'dev_repo', 'dev_jira_component', 'dev_docs', 'dev_api_is_public']

        if self.compliance_applicable:
            ret += list(ComponentVersion.get_compliance_fields())

        if self.op_applicable:
            ret += list(ComponentVersion.get_operations_fields()) + ['op_safe_restart']

        if self.mt_applicable:
            ret += list(ComponentVersion.get_maintenance_fields())

        if self.qa_applicable:
            ret += list(ComponentVersion.get_quality_assurance_fields())

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

        for f in (self._update_mt_rating, self._update_op_rating, self._update_qa_rating, self._update_compliance_rating):
            r, mr, br = f()
            rating += r
            max_rating += mr
            bad_rating += br

        self.meta_rating = int(100 * rating / max_rating)
        self.meta_bad_rating_fields = ", ".join(bad_rating)

    def save(self, *args, **kwargs):
        self._update_profile_completeness()
        self._update_rating()
        self.meta_update_date = datetime.datetime.now()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return "#%d %s - %s" % (self.id, self.component.name, self.version)


class ComponentDependency(models.Model):
    type = models.CharField(max_length=16, choices=DEPENDENCY_TYPE, default=DEPENDENCY_TYPE[0][0])
    component = models.ForeignKey(Component, on_delete=models.PROTECT)
    version = models.ForeignKey(ComponentVersion, on_delete=models.PROTECT)
    notes = fields.SmartTextField("Dependency notes")


##################################################################################################
# Deployments, products, etc
##################################################################################################

class DeploymentLocationClass(models.Model):
    name = models.CharField(max_length=64, help_text="global, per-datacenter, customer, endpoint")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class DeploymentEnvironment(models.Model):
    name = models.CharField(max_length=64, help_text="K8S, Windows VM, Linux VM,...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class TCPPort(models.Model):
    name = models.CharField(max_length=64, help_text="TCP/IP port name: HTTP, SSH, ...")
    port = models.IntegerField(help_text="TCP/IP port: 80, 21, ...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentDeployment(models.Model):
    name = models.CharField(max_length=64, help_text="Component deployment type: Cloud Account Server")
    location_class = models.ManyToManyField(DeploymentLocationClass)
    environment = models.ForeignKey(DeploymentEnvironment, on_delete=models.PROTECT)
    component_version = models.ForeignKey(ComponentVersion, on_delete=models.PROTECT)
    service_name = models.CharField(max_length=64, help_text="accsrv, taskmngr", blank=True)
    binary_name = models.CharField(max_length=64, help_text="accsrv.exe", blank=True)
    open_ports = models.ManyToManyField(TCPPort)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ProductFamily(models.Model):
    name = models.CharField(max_length=64, help_text="Product family")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class Product(models.Model):
    name = models.CharField(max_length=64, help_text="Product")
    family = models.ForeignKey(ProductFamily, on_delete=models.PROTECT)
    order = models.IntegerField(help_text="sorting order")
    components_deployments = models.ManyToManyField(ComponentDeployment)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)

class Datacenter(models.Model):
    name = models.CharField(max_length=64, help_text="Datacenter name")
    info = fields.SmartTextField("Info link")
    grafana = fields.SmartTextField("Grafana link")
    metrics = fields.SmartTextField("Metrics link")
    components_deployments = models.ManyToManyField(ComponentDeployment)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)
