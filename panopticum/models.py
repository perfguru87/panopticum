from django.db import models
from datatableview.views import DatatableView
from datatableview import helpers


class DatacenterModel(models.Model):
    name = models.CharField(max_length=64, help_text="Datacenter name")
    info = models.URLField(help_text="Info link", blank=True, null=True)
    grafana = models.URLField(help_text="Grafana link", blank=True, null=True)
    metrics = models.URLField(help_text="Grafana link", blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentLocationClassModel(models.Model):
    name = models.CharField(max_length=64, help_text="Global, Datacenter, Customer, Endpoint")
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentDataPrivacyClassModel(models.Model):
    name = models.CharField(max_length=64, help_text="Infrastructure, Metadata management, Data management, Application")
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


class DeploymentTypeModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component deployment type: k8s, Virtuozzo CT, Virtuozzo VM")

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

    class Meta:
        ordering = ['order']

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


class OSFamilyModel(models.Model):
    name = models.CharField(max_length=64, help_text="Linux, Windows, OSX, Solaris")

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


class TCPPortModel(models.Model):
    name = models.CharField(max_length=64, help_text="TCP/IP port name: HTTP, SSH, ...")
    port = models.IntegerField(help_text="TCP/IP port: 80, 21, ...")

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


LIFE_STATUS = (
    ('unknown', "?"),
    ('new', "New"),
    ('mature', "Mature"),
    ('legacy', "Legacy"),
    ('eol', "End Of Life"),
    ('eos', "End Of Support"),
)

LOW_MODERATE_GOOD = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('none', "None"),
    ('low', "Low"),
    ('moderate', "Moderate"),
    ('good', "Good"),
    ('excellent', "Excellent")
)

NO_PARTIAL_YES = (
    ('unknown', "?"),
    ('n/a', "N/A"),
    ('no', "No"),
    ('partial', "Partial"),
    ('yes', "Yes")
)


class TestingModel(models.Model):
    name = models.CharField(max_length=64, help_text="n/a, pre-commit, bvt, daily, weekly, manually")
    order = models.IntegerField(help_text="sorting order")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


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


class ComponentModel(models.Model):
    name = models.CharField(max_length=64, help_text="Component short name")
    description = models.TextField(blank=True, null=True)

    runtime_type = models.ForeignKey(ComponentRuntimeTypeModel, on_delete=models.PROTECT)
    data_privacy_class = models.ForeignKey(ComponentDataPrivacyClassModel, on_delete=models.PROTECT)
    location_class = models.ManyToManyField(ComponentLocationClassModel)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.PROTECT)
    subcategory = models.ForeignKey(ComponentSubcategoryModel, blank=True, null=True, on_delete=models.PROTECT)

    vendor = models.ForeignKey(SoftwareVendorModel, on_delete=models.PROTECT)
    datacenter = models.ManyToManyField(DatacenterModel, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "#%d %s" % (self.id, self.name)


class ComponentVersionModel(models.Model):
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, null=True)

    product = models.ManyToManyField(ProductModel, help_text="note: product can be linked to only one version of component",
                                     blank=True, null=True)

    # dependencies
    depends_on = models.ManyToManyField(ComponentModel, related_name='component_blocks', blank=True, null=True)

    # ownership
    owner_maintainer = models.ForeignKey(PersonModel, related_name='maintainer_of', on_delete=models.PROTECT, blank=True, null=True)
    owner_responsible_qa = models.ForeignKey(PersonModel, related_name='responsible_qa_of', on_delete=models.PROTECT, blank=True, null=True)
    owner_product_manager = models.ManyToManyField(PersonModel, related_name='product_manager_of', blank=True, null=True)
    owner_program_manager = models.ManyToManyField(PersonModel, related_name='program_managed_of', blank=True, null=True)
    owner_escalation_list = models.ManyToManyField(PersonModel, related_name='escalation_list_of', blank=True, null=True)
    owner_expert = models.ManyToManyField(PersonModel, related_name='expert_of', blank=True, null=True)
    owner_architect = models.ManyToManyField(PersonModel, related_name='architect_of', blank=True, null=True)

    # development
    dev_life_status = models.CharField(max_length=16, choices=LIFE_STATUS, blank=True, null=True)
    dev_language = models.ManyToManyField(ProgrammingLanguageModel, blank=True, null=True)
    dev_framework = models.ManyToManyField(FrameworkModel, blank=True, null=True)
    dev_database = models.ManyToManyField(DatabaseVendorModel, blank=True, null=True)
    dev_orm = models.ManyToManyField(ORMModel, blank=True, null=True)
    dev_logging = models.ManyToManyField(LoggerModel, blank=True, null=True)
    dev_raml = models.URLField(help_text="RAML link", blank=True, null=True)
    dev_repo = models.URLField(help_text="Repository", blank=True, null=True)
    dev_api_guideline_compliance = models.CharField(max_length=16, choices=NO_PARTIAL_YES, blank=True, null=True)
    dev_api_is_public = models.CharField(max_length=16, choices=NO_PARTIAL_YES, blank=True, null=True)
    dev_autotests_report = models.URLField(help_text="Autotests report link", blank=True, null=True)
    dev_jira_component = models.URLField(help_text="JIRA component", blank=True, null=True)
    dev_build_jenkins_job = models.URLField(help_text="Jenkins job to build the component", blank=True, null=True)
    dev_documentation = models.URLField(help_text="Documentation entry page", blank=True, null=True)

    # compliance
    compliance_fips = models.BooleanField(help_text="FIPS compliance")
    compliance_gdpr = models.BooleanField(help_text="GDPR compliance")

    # operational information
    op_deployment_name = models.CharField(max_length=64, blank=True, null=True)
    op_deployment_type = models.ManyToManyField(DeploymentTypeModel, blank=True, null=True)
    op_open_port = models.ManyToManyField(TCPPortModel, blank=True, null=True)
    op_binary_name = models.CharField(max_length=64, blank=True, null=True)
    op_anonymization_support = models.BooleanField(help_text="Is anonymisation supported?", blank=True, null=True)
    op_metrics = models.BooleanField(help_text="Metrics availability")
    op_guide_link = models.URLField(help_text="Operations guide link", blank=True, null=True)
    op_sla_doc_link = models.URLField(help_text="SLA/SLO documentation link", blank=True, null=True)
    op_capacity_doc_link = models.URLField(help_text="Capacity planning document", blank=True, null=True)
    op_backup_doc_link = models.URLField(help_text="Backup guide description", blank=True, null=True)
    op_safe_restart = models.BooleanField(help_text="Is it safe to restart?")
    op_safe_delete = models.BooleanField(help_text="Is it safe to delete?")
    op_safe_redeploy = models.BooleanField(help_text="Is it safe to redeploy?")
    op_horizontal_scalability = models.BooleanField(help_text="Horizontal scalability?")
    op_high_availability = models.BooleanField(help_text="High availability?")
    op_zero_downtime_upgrade = models.BooleanField(help_text="Zero-downtime upgrade")

    # quality assurance
    qa_manual_tests_link = models.URLField(help_text="Manual tests link", blank=True, null=True)
    qa_manual_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_manual_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='manual_tests', blank=True, null=True)

    qa_unit_tests_link = models.URLField(help_text="Unit tests link", blank=True, null=True)
    qa_unit_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True)
    qa_unit_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='unit_tests', blank=True, null=True)

    qa_e2e_tests_link = models.URLField(help_text="E2E tests link", blank=True, null=True)
    qa_e2e_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_e2e_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='e2e_tests', blank=True, null=True)

    qa_perf_tests_link = models.URLField(help_text="Performance tests link", blank=True, null=True)
    qa_perf_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_perf_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='perf_tests', blank=True, null=True)

    qa_longhaul_tests_link = models.URLField(help_text="Long haul tests link", blank=True, null=True)
    qa_longhaul_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_longhaul_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='longhaul_tests', blank=True, null=True)

    qa_security_tests_link = models.URLField(help_text="Security tests link", blank=True, null=True)
    qa_security_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_security_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='security_tests', blank=True, null=True)

    qa_api_tests_link = models.URLField(help_text="API tests link", blank=True, null=True)
    qa_api_tests_quality = models.CharField(max_length=16, choices=LOW_MODERATE_GOOD, blank=True, null=True)
    qa_api_tests_model = models.ForeignKey(TestingModel, on_delete=models.PROTECT, related_name='api_tests', blank=True, null=True)

    # meta
    meta_update_by = models.ForeignKey(PersonModel, on_delete=models.PROTECT, blank=True, null=True)
    meta_update_date = models.DateTimeField()
    meta_deleted = models.BooleanField()

    class Meta:
        ordering = ['-version']

    def __str__(self):
        return "#%d %s - %s" % (self.id, self.component.name, self.version)
