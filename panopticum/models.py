import django.forms
from django.db import models
from datatableview.views import DatatableView
from datatableview import helpers
from django.forms.models import model_to_dict
import datetime
from django.contrib.auth.models import AbstractUser, Group
from simple_history.models import HistoricalRecords

import panopticum.fields

class User(AbstractUser):
    dn = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=64, blank=True, null=True)
    photo = models.ImageField(upload_to='avatars')
    organization = models.ForeignKey('OrganizationModel', on_delete=models.PROTECT, blank=True,
                                     null=True)
    department = models.ForeignKey('OrgDepartmentModel', on_delete=models.PROTECT, blank=True,
                                   null=True)
    role = models.ForeignKey('PersonRoleModel', on_delete=models.PROTECT, blank=True, null=True)
    office_phone = models.CharField(max_length=64, blank=True, null=True)
    mobile_phone = models.CharField(max_length=64, blank=True, null=True)
    active_directory_guid = models.CharField(max_length=64, blank=True, null=True)
    employee_number = models.CharField(max_length=64, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    hidden = models.BooleanField(help_text="Hide the person from the potential assignee lists",
                                 db_index=True, default=False)
    manager = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)

    @property
    def photo_url(self):
        if self.photo and hasattr(self.photo, 'url'):
            return self.photo.url


##################################################################################################
# People, Org chart
##################################################################################################


class CountryModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s - #%d" % (self.name, self.id)


class OrgDepartmentModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s - #%d" % (self.name, self.id)


class OrganizationModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s - #%d" % (self.name, self.id)


class PersonRoleModel(models.Model):
    name = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s - #%d" % (self.name, self.id)


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


class ComponentDataPrivacyClassModel(models.Model):
    name = models.CharField(max_length=64,
                            help_text="Data Access, Secrets Management, Sensitive Metadata, Non-sensitive Metadata")
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "%s (order %d)" % (self.name, self.order)


class ComponentCategoryModel(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "%s (order %d)" % (self.name, self.order)


class ComponentSubcategoryModel(models.Model):
    name = models.CharField(max_length=64, help_text="Platform, Search engine, ...")
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class SoftwareVendorModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component vendor: OpenSource, MyCompany, ...")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class DatabaseVendorModel(models.Model):
    name = models.CharField(max_length=64, help_text="Database vendor: MSSQl, Oracle, SQLite, PostgreSQL, MySQL, Percona")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ProgrammingLanguageModel(models.Model):
    name = models.CharField(max_length=64, help_text="Programming language")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class FrameworkModel(models.Model):
    name = models.CharField(max_length=64, help_text="Framework")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ORMModel(models.Model):
    name = models.CharField(max_length=64, help_text="ORM")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class LoggerModel(models.Model):
    name = models.CharField(max_length=64, help_text="Logger model")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ComponentRuntimeTypeModel(models.Model):
    name = models.CharField(max_length=64, help_text="Library, Framework, Driver, OS Service, OS Process, Web Service, Database, MQ")
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "%s" % self.name


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
        return "%s" % self.name


class RequirementStatusType(models.Model):
    """ Who owner of that status? Component owner or signee or somebody else """
    owner = models.CharField(max_length=24)


class RequirementStatus(models.Model):
    """ Base model for Requirement status. That model describe only various statuses. """
    name = models.CharField(max_length=20, unique=True)  # yes, no, ready ...
    description = models.TextField(null=True, blank=True, max_length=255) # ready status is mean ...
    allow_for = models.ManyToManyField('RequirementStatusType') # restrict access for status by owner
                                                                # for example singee doesn't permitted to set status 'n/a'


class RequirementStatusEntry(models.Model):
    """ instance of status with value and owner type equal cell in widget at frontend side """
    status = models.ForeignKey(RequirementStatus, on_delete=models.CASCADE)
    type = models.ForeignKey(RequirementStatusType, on_delete=models.CASCADE) # component owner or signee
    requirement = models.ForeignKey('Requirement', related_name='statuses', on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True, max_length=16*pow(2, 10))
    component_version = models.ForeignKey('ComponentVersionModel', related_name='statuses', on_delete=models.CASCADE)

    class Meta:
        unique_together = ['status', 'type', 'component_version', 'requirement']
        permissions = [
            ("change_owner_status", "Can change component owner status"),
            ("change_signee_status", "Can change signee status")
        ]

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.status.name} ({self.status.type.name})"


class Requirement(models.Model):
    """ base model for requirement equal requirement header in widget """
    title = models.CharField(max_length=30, unique=True)  # backup, logging storage
    description = models.TextField(max_length=1024)  # that requirements about ...


    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.title}"

    def __str__(self):
        return self.__unicode__()


class RequirementSet(models.Model):
    """ Container for requirements. Example of usage: various requirement widgets at frontend """
    name = models.CharField(max_length=30, unique=True)
    requirements = models.ManyToManyField(Requirement, related_name='sets')
    description = models.TextField(null=True, blank=True)
    #
    owner_groups = models.ManyToManyField(Group, related_name='owner_groups', blank=True)

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __str__(self):
        return self.__unicode__()


class ComponentVersionModel(models.Model):
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, verbose_name="Version or build",
                               help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    # dependencies

    depends_on = models.ManyToManyField(ComponentModel, related_name='dependee', through='ComponentDependencyModel')

    # ownership

    owner_maintainer = models.ForeignKey(User, related_name='maintainer_of', on_delete=models.PROTECT, blank=True, null=True)
    owner_responsible_qa = models.ForeignKey(User, related_name='responsible_qa_of',
                                             on_delete=models.PROTECT, blank=True, null=True)
    owner_product_manager = models.ManyToManyField(User, related_name='product_manager_of', blank=True)
    owner_program_manager = models.ManyToManyField(User, related_name='program_managed_of', blank=True)
    owner_escalation_list = models.ManyToManyField(User, related_name='escalation_list_of', blank=True)
    owner_expert = models.ManyToManyField(User, related_name='expert_of', blank=True)
    owner_architect = models.ManyToManyField(User, related_name='architect_of', blank=True)

    # development

    dev_language = models.ManyToManyField(ProgrammingLanguageModel, verbose_name="Language", blank=True)
    dev_framework = models.ManyToManyField(FrameworkModel, verbose_name="Frameworks", blank=True)
    dev_database = models.ManyToManyField(DatabaseVendorModel, verbose_name="Supported Databases", blank=True)
    dev_orm = models.ManyToManyField(ORMModel, verbose_name="ORM", blank=True)
    dev_logging = models.ManyToManyField(LoggerModel, verbose_name="Logging framework", blank=True)

    dev_raml = panopticum.fields.SmartTextField("RAML link", help_text="Multiple links allowed")
    dev_repo = panopticum.fields.SmartTextField("Repository", help_text="Multiple links allowed")
    dev_public_repo = panopticum.fields.SmartTextField("Public Repository", help_text="Multiple links allowed")
    dev_jira_component = panopticum.fields.SmartTextField("JIRA component", help_text="Multiple links allowed")
    dev_build_jenkins_job = panopticum.fields.SmartTextField("Jenkins job to build the component", help_text="Multiple links allowed")
    dev_docs = panopticum.fields.SmartTextField("Documentation entry page", help_text="Multiple links allowed")
    dev_public_docs = panopticum.fields.SmartTextField("Public Documentation", help_text="Multiple links allowed")
    dev_commit_link = panopticum.fields.SmartTextField("Commit link", help_text="Multiple links allowed")

    dev_api_is_public = panopticum.fields.NoPartialYesField("API is public")

    # TODO: deprecated. Let's remove
    # compliance

    compliance_applicable = models.BooleanField(verbose_name="Compliance requirements are applicable", default=True)

    compliance_fips_status = panopticum.fields.NoPartialYesField("FIPS compliance")
    compliance_fips_notes = panopticum.fields.SmartTextField("FIPS compliance notes")
    compliance_fips_signoff = panopticum.fields.SigneeField(related_name='signed_fips')

    compliance_gdpr_status = panopticum.fields.NoPartialYesField("GDPR compliance")
    compliance_gdpr_notes = panopticum.fields.SmartTextField("GDRP compliance notes")
    compliance_gdpr_signoff = panopticum.fields.SigneeField(related_name='signed_gdpr')

    compliance_api_status = panopticum.fields.NoPartialYesField("API guildeine compliance")
    compliance_api_notes = panopticum.fields.SmartTextField("API guideline compliance notes")
    compliance_api_signoff = panopticum.fields.SigneeField(related_name='signed_api_guideline')

    # TODO: deprecated. Let's remove
    # operational readiness information

    op_applicable = models.BooleanField(verbose_name="Operational requirements are applicable", default=True)

    op_guide_status = panopticum.fields.NoPartialYesField("Operations guide")
    op_guide_notes = panopticum.fields.SmartTextField("Operations guide notes")
    op_guide_signoff = panopticum.fields.SigneeField(related_name='signed_op_guide')

    op_failover_status = panopticum.fields.NoPartialYesField("Failover")
    op_failover_notes = panopticum.fields.SmartTextField("Failover notes")
    op_failover_signoff = panopticum.fields.SigneeField(related_name='signed_failover')

    op_horizontal_scalability_status = panopticum.fields.NoPartialYesField("Horizontal scalability")
    op_horizontal_scalability_notes = panopticum.fields.SmartTextField("Horizontal scalability notes")
    op_horizontal_scalability_signoff = panopticum.fields.SigneeField(related_name='signed_horizontal_scalability')

    op_scaling_guide_status = panopticum.fields.NoPartialYesField("Scaling guide")
    op_scaling_guide_notes = panopticum.fields.SmartTextField("Scaling guide notes")
    op_scaling_guide_signoff = panopticum.fields.SigneeField(related_name='signed_scaling_guide')

    op_sla_guide_status = panopticum.fields.NoPartialYesField("SLA/SLO guide")
    op_sla_guide_notes = panopticum.fields.SmartTextField("SLA/SLO guide notes")
    op_sla_guide_signoff = panopticum.fields.SigneeField(related_name='signed_sla_guide')

    op_metrics_status = panopticum.fields.NoPartialYesField("Monitoring")
    op_metrics_notes = panopticum.fields.SmartTextField("Monitoring notes")
    op_metrics_signoff = panopticum.fields.SigneeField(related_name='signed_metrics')

    op_alerts_status = panopticum.fields.NoPartialYesField("Alerts guide")
    op_alerts_notes = panopticum.fields.SmartTextField("Alerts guide notes")
    op_alerts_signoff = panopticum.fields.SigneeField(related_name='signed_alerts')

    op_zero_downtime_status = panopticum.fields.NoPartialYesField("Zero-downtime upgrade")
    op_zero_downtime_notes = panopticum.fields.SmartTextField("Zero-downtime upgrade notes")
    op_zero_downtime_signoff = panopticum.fields.SigneeField(related_name='signed_zero_downtime')

    op_backup_status = panopticum.fields.NoPartialYesField("Backup")
    op_backup_notes = panopticum.fields.SmartTextField("Backup notes")
    op_backup_signoff = panopticum.fields.SigneeField(related_name='signed_backup')

    op_safe_restart = models.BooleanField(help_text="Is it safe to restart?", blank=True, null=True)
    op_safe_delete = models.BooleanField(help_text="Is it safe to delete?", blank=True, null=True)
    op_safe_redeploy = models.BooleanField(help_text="Is it safe to redeploy?", blank=True, null=True)

    # TODO: deprecated. Let's remove
    # maintainability

    mt_applicable = models.BooleanField(verbose_name="Maintainability requirements are applicable", default=True)

    mt_http_tracing_status = panopticum.fields.NoPartialYesField("HTTP requests tracing", help_text="HTTP request b3 propagation support")
    mt_http_tracing_notes = panopticum.fields.SmartTextField("HTTP requests tracing notes")
    mt_http_tracing_signoff = panopticum.fields.SigneeField(related_name='signed_http_tracing')

    mt_logging_completeness_status = panopticum.fields.NoPartialYesField("Logging completeness", help_text="Are logs sufficient?")
    mt_logging_completeness_notes = panopticum.fields.SmartTextField("Logging completeness notes")
    mt_logging_completeness_signoff = panopticum.fields.SigneeField(related_name='signed_logging_completeness')

    mt_logging_format_status = panopticum.fields.NoPartialYesField("Logging format", help_text="Logs have proper format")
    mt_logging_format_notes = panopticum.fields.SmartTextField("Logging format notes")
    mt_logging_format_signoff = panopticum.fields.SigneeField(related_name='signed_logging_format')

    mt_logging_storage_status = panopticum.fields.NoPartialYesField("Logging storage", help_text="Is proper logs storage used?")
    mt_logging_storage_notes = panopticum.fields.SmartTextField("Logging storage notes")
    mt_logging_storage_signoff = panopticum.fields.SigneeField(related_name='signed_logging_storage')

    mt_logging_sanitization_status = panopticum.fields.NoPartialYesField("Logs sanitization", help_text="Logs do not have sensitive information")
    mt_logging_sanitization_notes = panopticum.fields.SmartTextField("Logging sanitization notes")
    mt_logging_sanitization_signoff = panopticum.fields.SigneeField(related_name='signed_logggin_sanitization')

    mt_db_anonymisation_status = panopticum.fields.NoPartialYesField("DataBase anonymisation")
    mt_db_anonymisation_notes = panopticum.fields.SmartTextField("DataBase anonymisation")
    mt_db_anonymisation_signoff = panopticum.fields.SigneeField(related_name='signed_db_anonymisation')

    # quality assurance

    qa_applicable = models.BooleanField(verbose_name="Tests requirements are applicable", default=True)

    qa_manual_tests_status = panopticum.fields.LowMedHighField("Manual tests", help_text="Completeness, coverage, quality")
    qa_manual_tests_notes = panopticum.fields.SmartTextField("Manual tests notes")
    qa_manual_tests_signoff = panopticum.fields.SigneeField(related_name='signed_manual_tests')

    qa_unit_tests_status = panopticum.fields.LowMedHighField("Unit tests", help_text="Completeness, coverage, quality")
    qa_unit_tests_notes = panopticum.fields.SmartTextField("Unit tests notes")
    qa_unit_tests_signoff = panopticum.fields.SigneeField(related_name='signed_unit_tests')

    qa_e2e_tests_status = panopticum.fields.LowMedHighField("E2E tests", help_text="Completeness, coverage, quality")
    qa_e2e_tests_notes = panopticum.fields.SmartTextField("E2E tests notes")
    qa_e2e_tests_signoff = panopticum.fields.SigneeField(related_name='signed_e2e_tests')

    qa_perf_tests_status = panopticum.fields.LowMedHighField("Performance tests", help_text="Completeness, coverage, quality")
    qa_perf_tests_notes = panopticum.fields.SmartTextField("Perf tests notes")
    qa_perf_tests_signoff = panopticum.fields.SigneeField(related_name='signed_perf_tests')

    qa_longhaul_tests_status = panopticum.fields.LowMedHighField("Long-haul tests", help_text="Completeness, coverage, quality")
    qa_longhaul_tests_notes = panopticum.fields.SmartTextField("Long-hault tests notes")
    qa_longhaul_tests_signoff = panopticum.fields.SigneeField(related_name='signed_longhaul_tests')

    qa_security_tests_status = panopticum.fields.LowMedHighField("Security tests", help_text="Completeness, coverage, quality")
    qa_security_tests_notes = panopticum.fields.SmartTextField("Security tests notes")
    qa_security_tests_signoff = panopticum.fields.SigneeField(related_name='signed_security_tests')

    qa_api_tests_status = panopticum.fields.LowMedHighField("API tests", help_text="Completeness, coverage, quality")
    qa_api_tests_notes = panopticum.fields.SmartTextField("API tests notes")
    qa_api_tests_signoff = panopticum.fields.SigneeField(related_name='signed_api_tests')

    qa_anonymisation_tests_status = panopticum.fields.LowMedHighField("DB anonymisation tests")
    qa_anonymisation_tests_notes = panopticum.fields.SmartTextField("DB anonymisation tests notes")
    qa_anonymisation_tests_signoff = panopticum.fields.SigneeField(related_name='signed_anonymisation_tests')

    qa_upgrade_tests_status = panopticum.fields.LowMedHighField("Upgrade tests", help_text="Functional, performance, real volume")
    qa_upgrade_tests_notes = panopticum.fields.SmartTextField("Upgrade tests notes")
    qa_upgrade_tests_signoff = panopticum.fields.SigneeField(related_name='signed_upgrade_tests')

    # meta

    meta_update_by = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, related_name='updater_of')
    meta_update_date = models.DateTimeField(db_index=True)
    meta_deleted = models.BooleanField(default=False)

    meta_compliance_rating = models.IntegerField(default=0)
    meta_mt_rating = models.IntegerField(default=0)
    meta_op_rating = models.IntegerField(default=0)
    meta_qa_rating = models.IntegerField(default=0)
    meta_rating = models.IntegerField(default=0)
    meta_profile_completeness = models.IntegerField(default=0)
    meta_profile_not_filled_fields = models.TextField(default="")
    meta_bad_rating_fields = models.TextField(default="")

    meta_locations = models.ManyToManyField('DeploymentLocationClassModel', help_text='cached component deployment locations',
                                            related_name='component_versions', blank=True)
    meta_product_versions = models.ManyToManyField('ProductVersionModel', help_text='cached product versions',
                                                   related_name='component_versions', blank=True)

    meta_searchstr_locations = models.TextField(blank=True)
    meta_searchstr_product_versions = models.TextField(blank=True)

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
                                       ComponentVersionModel.get_compliance_fields())

    def _update_mt_rating(self):
        return self._update_any_rating('meta_mt_rating', 'mt_applicable', NO_PARTIAL_YES_RATING,
                                       ComponentVersionModel.get_maintenance_fields())

    def _update_op_rating(self):
        return self._update_any_rating('meta_op_rating', 'op_applicable', NO_PARTIAL_YES_RATING,
                                       ComponentVersionModel.get_operations_fields())

    def _update_qa_rating(self):
        return self._update_any_rating('meta_qa_rating', 'qa_applicable', LOW_MED_HIGH_RATING,
                                       ComponentVersionModel.get_quality_assurance_fields())

    def _get_profile_must_fields(self):
        ret = ['owner_maintainer', 'owner_responsible_qa', 'owner_product_manager', 'owner_program_manager',
                'owner_escalation_list', 'owner_expert', 'owner_architect',
                'dev_language', 'dev_raml', 'dev_repo', 'dev_jira_component', 'dev_docs', 'dev_api_is_public']

        if self.compliance_applicable:
            ret += list(ComponentVersionModel.get_compliance_fields())

        if self.op_applicable:
            ret += list(ComponentVersionModel.get_operations_fields()) + ['op_safe_restart']

        if self.mt_applicable:
            ret += list(ComponentVersionModel.get_maintenance_fields())

        if self.qa_applicable:
            ret += list(ComponentVersionModel.get_quality_assurance_fields())

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

    def update_meta_locations_and_product_versions(self):
        locations = {}
        product_versions = {}

        for d in ComponentDeploymentModel.objects.filter(component_version=self):
            locations[d.location_class.id] = d.location_class
            product_versions[d.product_version.id] = d.product_version

        self.meta_locations.set(locations.values())
        self.meta_product_versions.set(product_versions.values())

        self.meta_searchstr_locations = ", ".join(["{%s}" % l.name for l in self.meta_locations.all()])
        self.meta_searchstr_product_versions = ", ".join(["{%s}" % p.name for p in self.meta_product_versions.all()])
        super().save()

    def save(self, *args, **kwargs):
        self._update_profile_completeness()
        self._update_rating()

        self.meta_update_date = datetime.datetime.now()
        super().save(*args, **kwargs)

        self.update_meta_locations_and_product_versions()

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return "%s - %s" % (self.component.name, self.version)


class ComponentDependencyModel(models.Model):
    type = models.CharField(max_length=16, choices=DEPENDENCY_TYPE, default=DEPENDENCY_TYPE[0][0])
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT)
    version = models.ForeignKey(ComponentVersionModel, on_delete=models.PROTECT)
    notes = panopticum.fields.SmartTextField("Dependency notes")


##################################################################################################
# Deployments, products, etc
##################################################################################################

class DeploymentLocationClassModel(models.Model):
    name = models.CharField(max_length=128, help_text="global, per-datacenter, customer, endpoint")
    shortname = models.CharField(max_length=64, unique=True, help_text="most useful by automation tools like data importer/exporter")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "%s" % self.name


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
        ordering = ['port']

    def __str__(self):
        return "%d %s" % (self.port, self.name)


class ProductFamilyModel(models.Model):
    name = models.CharField(max_length=64, help_text="Product family")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ProductVersionModel(models.Model):
    shortname = models.CharField(max_length=64, help_text="Product version short name")
    name = models.CharField(max_length=64, help_text="Product version full name")
    family = models.ForeignKey(ProductFamilyModel, on_delete=models.PROTECT)
    order = models.IntegerField(help_text="sorting order")

    def _update_components_meta_searchstr(self):
        if not self.id:
            return

        super().save()
        for d in ComponentDeploymentModel.objects.filter(product_version=self):
            d.component_version.update_meta_locations_and_product_versions()

    def save(self, *args, **kwargs):
        self._update_components_meta_searchstr()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "%s" % (self.name)


class ComponentDeploymentModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component deployment name: Cloud Account Server",
                            verbose_name="Deployment name", blank=True)
    location_class = models.ForeignKey(DeploymentLocationClassModel, on_delete=models.PROTECT)
    product_version = models.ForeignKey(ProductVersionModel, on_delete=models.PROTECT)
    environment = models.ForeignKey(DeploymentEnvironmentModel, on_delete=models.PROTECT)
    component_version = models.ForeignKey(ComponentVersionModel, on_delete=models.PROTECT)
    service_name = models.CharField(max_length=64, help_text="accsrv, taskmngr", blank=True)
    binary_name = models.CharField(max_length=64, help_text="accsrv.exe", blank=True)
    open_ports = models.ManyToManyField(TCPPortModel, blank=True)
    notes = panopticum.fields.SmartTextField("Deployment notes")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.component_version.update_meta_locations_and_product_versions()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s - %s %s%s" % (self.product_version.shortname, self.component_version.component.name, self.component_version.version,
                                 (" (%s)" % self.name) if self.name else "")


class DatacenterModel(models.Model):
    name = models.CharField(max_length=64, help_text="Datacenter name")
    info = panopticum.fields.SmartTextField("Info link")
    grafana = panopticum.fields.SmartTextField("Grafana link")
    metrics = panopticum.fields.SmartTextField("Metrics link")
    components_deployments = models.ManyToManyField(ComponentDeploymentModel)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name
