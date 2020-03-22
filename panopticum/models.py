import django.forms
from django.db import models
from datatableview.views import DatatableView
from datatableview import helpers
from django.forms.models import model_to_dict
import datetime
from django.contrib.auth.models import AbstractUser, Group
from simple_history.models import HistoricalRecords

import panopticum.fields

# constants from fixtures
NOT_APP_STATUS = 4
POSITIVE_STATUS = 3
NEGATIVE_STATUS = 2
UNKNOWN_STATUS = 1
SIGNEE_STATUS_TYPE = 2

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
        ordering = ['order', 'name']

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
        verbose_name = 'Programming language'
        verbose_name_plural = 'Programming language'
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class FrameworkModel(models.Model):
    name = models.CharField(max_length=64, help_text="Framework")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)
    notes = panopticum.fields.SmartTextField("Notes", help_text="Framework notes")

    class Meta:
        verbose_name = 'Framework'
        verbose_name_plural = 'Frameworks'
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class RuntimeModel(models.Model):
    name = models.CharField(max_length=64, help_text="Runtime: e.g. C++/Python/Go runtime")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Runtime'
        verbose_name_plural = 'Runtimes'
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ORMModel(models.Model):
    name = models.CharField(max_length=64, help_text="ORM")
    language = models.ForeignKey(ProgrammingLanguageModel, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Object-Relational Mapping'
        verbose_name_plural = 'Object-Relational Mappings'
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class LoggerModel(models.Model):
    name = models.CharField(max_length=64, help_text="Logger model")

    class Meta:
        verbose_name = 'Logger'
        verbose_name_plural = 'Loggers'
        ordering = ['name']

    def __str__(self):
        return "%s" % self.name


class ComponentType(models.Model):
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
    type = models.ForeignKey(ComponentType, on_delete=models.PROTECT)
    data_privacy_class = models.ForeignKey(ComponentDataPrivacyClassModel, on_delete=models.PROTECT)
    category = models.ForeignKey(ComponentCategoryModel, on_delete=models.PROTECT, related_name='components')
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
    history = HistoricalRecords()

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
        return f"{self.sets.first().name}: {self.title}" if self.sets.exists() else f"{__class__.__name__}: {self.title}"

    def __str__(self):
        return self.__unicode__()


class RequirementSet(models.Model):
    """ Container for requirements. Example of usage: various requirement widgets at frontend """
    name = models.CharField(max_length=30, unique=True)
    requirements = models.ManyToManyField(Requirement, related_name='sets')
    description = models.TextField(null=True, blank=True)
    doc_link = models.URLField("Documentation link URL", max_length=4096, blank=True)
    #
    owner_groups = models.ManyToManyField(Group, related_name='owner_groups', blank=True)

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __str__(self):
        return self.__unicode__()


class ComponentManager(models.Manager):

    def with_rating(self, requirement_set_id=None):
        """ Custom manager method for add calculated fields: total_statuses, positive_status_count,
         negative_status_count, unknown_status_count. That useful for calculation overal component
         version status """
        annotate_filter_kwargs = dict(statuses__type=SIGNEE_STATUS_TYPE)

        if requirement_set_id:
            requirement_count = RequirementSet.objects.get(pk=requirement_set_id).requirements.count()
            annotate_filter_kwargs.update({'statuses__requirement__sets': requirement_set_id})
        else:
            requirement_count = RequirementSet.objects.all().aggregate(count=django.db.models.Count('requirements'))['count']
        return self.model.objects.annotate(
            rating= 100 * django.db.models.Count('statuses',
                                         filter=django.db.models.Q(statuses__status=POSITIVE_STATUS,
                                                                   **annotate_filter_kwargs),
                                         output_field=django.db.models.FloatField())
                  / requirement_count,
            total_statuses = django.db.models.Count('statuses',
                                                   filter=django.db.models.Q(**annotate_filter_kwargs)),
            positive_status_count=django.db.models.Count('statuses',
                                                   filter=django.db.models.Q(statuses__status=POSITIVE_STATUS,
                                                                             **annotate_filter_kwargs)),
            negative_status_count = django.db.models.Count('statuses',
                                                     filter=django.db.models.Q(statuses__status=NEGATIVE_STATUS,
                                                                               **annotate_filter_kwargs)),
            unknown_status_count = django.db.models.Count('statuses',
                                                     filter=django.db.models.Q(statuses__status=UNKNOWN_STATUS,
                                                                               **annotate_filter_kwargs))
        )


class ComponentVersionModel(models.Model):
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, verbose_name="Version or build",
                               help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, null=True)
    history = HistoricalRecords()
    objects = ComponentManager()

    # dependencies

    depends_on = models.ManyToManyField(ComponentModel, related_name='dependee', through='ComponentDependencyModel')

    # ownership

    owner_maintainer = models.ForeignKey(User, related_name='maintainer_of',
                                         on_delete=models.PROTECT, verbose_name="Maintainer", blank=True, null=True)
    owner_responsible_qa = models.ForeignKey(User, related_name='responsible_qa_of', verbose_name="Responsible QA",
                                             on_delete=models.PROTECT, blank=True, null=True)
    owner_product_manager = models.ManyToManyField(User, related_name='product_manager_of',
                                                   verbose_name="Product Managers", blank=True)
    owner_program_manager = models.ManyToManyField(User, related_name='program_managed_of',
                                                   verbose_name="Program Managers", blank=True)
    owner_escalation_list = models.ManyToManyField(User, related_name='escalation_list_of',
                                                   verbose_name="Escalation list", blank=True)
    owner_expert = models.ManyToManyField(User, related_name='expert_of', verbose_name="Experts", blank=True)
    owner_architect = models.ManyToManyField(User, related_name='architect_of', verbose_name="Architects", blank=True)

    # development
    links_help_msg = "List of URLs separated by whitespace"

    dev_language = models.ManyToManyField(ProgrammingLanguageModel, verbose_name="Language", blank=True)
    dev_framework = models.ManyToManyField(FrameworkModel, verbose_name="Frameworks", blank=True)
    dev_database = models.ManyToManyField(DatabaseVendorModel, verbose_name="Supported Databases", blank=True)
    dev_orm = models.ManyToManyField(ORMModel, verbose_name="ORM", blank=True)
    dev_logging = models.ManyToManyField(LoggerModel, verbose_name="Logging framework", blank=True)

    dev_raml = panopticum.fields.SmartTextField("RAML link", help_text=links_help_msg)
    dev_repo = panopticum.fields.SmartTextField("Repository", help_text=links_help_msg)
    dev_public_repo = panopticum.fields.SmartTextField("Public Repository", help_text=links_help_msg)
    dev_jira_component = panopticum.fields.SmartTextField("JIRA component", help_text=links_help_msg)
    dev_build_jenkins_job = panopticum.fields.SmartTextField("Jenkins job to build the component", help_text=links_help_msg)
    dev_docs = panopticum.fields.SmartTextField("Documentation entry page", help_text=links_help_msg)
    dev_public_docs = panopticum.fields.SmartTextField("Public Documentation", help_text=links_help_msg)
    dev_commit_link = panopticum.fields.SmartTextField("Commit link", help_text=links_help_msg)

    dev_api_is_public = panopticum.fields.NoPartialYesField("API is public")


    # quality assurance
    test_status_help_msg = "Subjective Dev/QA lead opinion on tests completeness, coverage, quality, etc"

    qa_applicable = models.BooleanField(verbose_name="Tests requirements are applicable", default=True)

    qa_manual_tests_status = panopticum.fields.LowMedHighField("Manual tests", help_text=test_status_help_msg)
    qa_manual_tests_notes = panopticum.fields.SmartTextField("Manual tests notes")
    qa_manual_tests_signoff = panopticum.fields.SigneeField(related_name='signed_manual_tests')

    qa_unit_tests_status = panopticum.fields.LowMedHighField("Unit tests", help_text=test_status_help_msg)
    qa_unit_tests_notes = panopticum.fields.SmartTextField("Unit tests notes")
    qa_unit_tests_signoff = panopticum.fields.SigneeField(related_name='signed_unit_tests')

    qa_e2e_tests_status = panopticum.fields.LowMedHighField("E2E tests", help_text=test_status_help_msg)
    qa_e2e_tests_notes = panopticum.fields.SmartTextField("E2E tests notes")
    qa_e2e_tests_signoff = panopticum.fields.SigneeField(related_name='signed_e2e_tests')

    qa_perf_tests_status = panopticum.fields.LowMedHighField("Performance tests", help_text=test_status_help_msg)
    qa_perf_tests_notes = panopticum.fields.SmartTextField("Perf tests notes")
    qa_perf_tests_signoff = panopticum.fields.SigneeField(related_name='signed_perf_tests')

    qa_longhaul_tests_status = panopticum.fields.LowMedHighField("Long-haul tests", help_text=test_status_help_msg)
    qa_longhaul_tests_notes = panopticum.fields.SmartTextField("Long-hault tests notes")
    qa_longhaul_tests_signoff = panopticum.fields.SigneeField(related_name='signed_longhaul_tests')

    qa_security_tests_status = panopticum.fields.LowMedHighField("Security tests", help_text=test_status_help_msg)
    qa_security_tests_notes = panopticum.fields.SmartTextField("Security tests notes")
    qa_security_tests_signoff = panopticum.fields.SigneeField(related_name='signed_security_tests')

    qa_api_tests_status = panopticum.fields.LowMedHighField("API tests", help_text=test_status_help_msg)
    qa_api_tests_notes = panopticum.fields.SmartTextField("API tests notes")
    qa_api_tests_signoff = panopticum.fields.SigneeField(related_name='signed_api_tests')

    qa_anonymisation_tests_status = panopticum.fields.LowMedHighField("DB anonymisation tests")
    qa_anonymisation_tests_notes = panopticum.fields.SmartTextField("DB anonymisation tests notes")
    qa_anonymisation_tests_signoff = panopticum.fields.SigneeField(related_name='signed_anonymisation_tests')

    qa_upgrade_tests_status = panopticum.fields.LowMedHighField("Upgrade tests", help_text="Functional, performance, real volume")
    qa_upgrade_tests_notes = panopticum.fields.SmartTextField("Upgrade tests notes")
    qa_upgrade_tests_signoff = panopticum.fields.SigneeField(related_name='signed_upgrade_tests')

    # meta
    update_date = models.DateTimeField(db_index=True, auto_now=True)
    deleted = models.BooleanField(default=False)

    meta_compliance_rating = models.IntegerField(default=0)
    meta_mt_rating = models.IntegerField(default=0)
    meta_op_rating = models.IntegerField(default=0)
    meta_qa_rating = models.IntegerField(default=0)
    meta_rating = models.IntegerField(default=0)
    meta_profile_completeness = models.IntegerField(default=0)
    meta_profile_not_filled_fields = models.TextField(default="")
    meta_bad_rating_fields = models.TextField(default="")

    # TODO: remove and switch to calculated field
    meta_locations = models.ManyToManyField('DeploymentLocationClassModel', help_text='cached component deployment locations',
                                            related_name='component_versions', blank=True)
    # TODO: remove and switch to calculated field
    meta_product_versions = models.ManyToManyField('ProductVersionModel', help_text='cached product versions',
                                                   related_name='component_versions', blank=True)
    # TODO: remove
    meta_searchstr_locations = models.TextField(blank=True)
    meta_searchstr_product_versions = models.TextField(blank=True)

    def _get_rating(self):
        max_status_rating = RequirementStatus.objects.aggregate(models.Max('rating'))['rating__max']
        rating = self.statuses.filter(requirement__sets=1, type=2) \
            .aggregate(rating__sum=models.Sum('status__rating'))['rating__sum']
        max_rating = self.statuses.filter(requirement__sets=1,
                                                       type=2).count() * max_status_rating
        return rating / max_rating

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
    def get_quality_assurance_fields():
        return ('qa_manual_tests_status', 'qa_unit_tests_status', 'qa_e2e_tests_status', 'qa_perf_tests_status',
                'qa_longhaul_tests_status', 'qa_security_tests_status', 'qa_api_tests_status',
                'qa_anonymisation_tests_status', 'qa_upgrade_tests_status')


    def _update_qa_rating(self):
        return self._update_any_rating('meta_qa_rating', 'qa_applicable', LOW_MED_HIGH_RATING,
                                       ComponentVersionModel.get_quality_assurance_fields())

    def _get_profile_must_fields(self):
        ret = ['owner_maintainer', 'owner_responsible_qa', 'owner_product_manager', 'owner_program_manager',
                'owner_escalation_list', 'owner_expert', 'owner_architect',
                'dev_language', 'dev_raml', 'dev_repo', 'dev_jira_component', 'dev_docs', 'dev_api_is_public']


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


    def update_meta_locations_and_product_versions(self): # TODO: remove and switch to calculated fields
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
    shortname = models.CharField(max_length=64, unique=True, null=True,
                                 help_text="most useful by automation tools like data importer/exporter")
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

    def _update_components_meta_searchstr(self): # TODO: remove and switch to calculated fields
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
    location_class = models.ForeignKey(DeploymentLocationClassModel,
                                       related_name='deployments',
                                       on_delete=models.PROTECT)
    product_version = models.ForeignKey(ProductVersionModel,
                                        related_name='deployments',
                                        on_delete=models.PROTECT)
    is_new_deployment = models.BooleanField(help_text="This component is new in given product", db_index=True, default=False)

    environment = models.ForeignKey(DeploymentEnvironmentModel,
                                    related_name='deployments',
                                    on_delete=models.PROTECT)
    component_version = models.ForeignKey(ComponentVersionModel,
                                          related_name='deployments',
                                          on_delete=models.PROTECT)
    runtime = models.ForeignKey(RuntimeModel,
                                related_name='deployments',
                                on_delete=models.PROTECT,
                                blank=True, null=True, default=None)
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
