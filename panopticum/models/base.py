import django.forms
from django.db import models
from datatableview.views import DatatableView
from datatableview import helpers
from django.forms.models import model_to_dict
import datetime
from django.contrib.auth.models import AbstractUser, Group
from simple_history.models import HistoricalRecords
import django_atlassian.models.djira

import panopticum.fields

# constants statuses from the fixtures
REQ_STATUS_UNKNOWN = 1
REQ_STATUS_NOT_READY = 2
REQ_STATUS_READY = 3
REQ_STATUS_NOT_APPLICABLE = 4
REQ_STATUS_WAITING_FOR_APPROVAL = 5
REQ_OWNER_STATUS = 1
REQ_SIGNEE_STATUS = 2
REQ_OVERALL_STATUS = 3

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
    ("strong_rw", "Runtime - Strong - R/W"),
    ("strong_ro", "Runtime - Strong - R/O"),
    ("strong_wo", "Runtime - Strong - W/O"),
    ("weak_rw", "Runtime - Weak - R/W"),
    ("weak_ro", "Runtime - Weak - R/O"),
    ("weak_wo", "Runtime - Weak - W/O"),
    ("compile_time", "Compile time"),
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


# proxy model for filtering components without component version in admin panel
class FilteredComponent(ComponentModel):
    class Meta:
        proxy = True


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


class ComponentVersionModel(models.Model):
    component = models.ForeignKey(ComponentModel, on_delete=models.PROTECT, related_name='component_version')

    version = models.CharField(max_length=64, verbose_name="Version or build",
                               help_text="note: component version instance will be cloned if you change version!")
    comments = models.TextField(blank=True, verbose_name="Version description", null=True)
    history = HistoricalRecords()

    # dependencies

    depends_on = models.ManyToManyField(ComponentModel, related_name='dependee', through='ComponentDependencyModel')

    # ownership

    owner_maintainer = models.ForeignKey(User, related_name='maintainer_of',
                                         on_delete=models.PROTECT, verbose_name="Maintainer", blank=True, null=True,
                                         help_text="Dev Lead or primary contributor")
    owner_responsible_qa = models.ForeignKey(User, related_name='responsible_qa_of', verbose_name="Responsible QA",
                                             on_delete=models.PROTECT, blank=True, null=True,
                                             help_text="QA Lead or primary QA expert")
    owner_product_manager = models.ManyToManyField(User, related_name='product_manager_of',
                                                   verbose_name="Product Managers", blank=True)
    owner_program_manager = models.ManyToManyField(User, related_name='program_managed_of',
                                                   verbose_name="Program Managers", blank=True)
    owner_escalation_list = models.ManyToManyField(User, related_name='escalation_list_of',
                                                   verbose_name="Escalation list", blank=True,
                                                   help_text="People who are in charge of RnD-side support in case of incidents")
    owner_expert = models.ManyToManyField(User, related_name='expert_of', verbose_name="Experts", blank=True,
                                          help_text="All people who have experience with given component")
    owner_architect = models.ManyToManyField(User, related_name='architect_of', verbose_name="Architects", blank=True,
                                             help_text="People who are in charge of the component architecture")

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
    dev_issuetracker_component = panopticum.fields.SmartTextField("Issue tracker component", help_text=links_help_msg)
    dev_build_jenkins_job = panopticum.fields.SmartTextField("Jenkins job to build the component", help_text=links_help_msg)
    dev_docs = panopticum.fields.SmartTextField("Documentation entry page", help_text=links_help_msg)
    dev_public_docs = panopticum.fields.SmartTextField("Public Documentation", help_text=links_help_msg)
    dev_commit_link = panopticum.fields.SmartTextField("Commit link", help_text=links_help_msg)

    dev_api_is_public = panopticum.fields.NoPartialYesField("API is public")

    # requirement sets
    excluded_requirement_set = models.ManyToManyField(RequirementSet, related_name='excluded_requirement_set_of', verbose_name='Excluded Requirement Sets', blank=True)

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
    meta_qa_rating = models.IntegerField(default=0)
    meta_rating = models.IntegerField(default=0)
    meta_profile_completeness = models.IntegerField(default=0)
    meta_profile_not_filled_fields = models.TextField(default="")
    meta_profile_not_signed_requirements = models.TextField(default="")

    # TODO: remove and switch to calculated field
    meta_locations = models.ManyToManyField('DeploymentLocationClassModel', help_text='cached component deployment locations',
                                            related_name='component_versions', blank=True)
    # TODO: remove and switch to calculated field
    meta_product_versions = models.ManyToManyField('ProductVersionModel', help_text='cached product versions',
                                                   related_name='component_versions', blank=True)
    # TODO: remove
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
    def get_quality_assurance_fields():
        return ('qa_manual_tests_status', 'qa_unit_tests_status', 'qa_e2e_tests_status', 'qa_perf_tests_status',
                'qa_longhaul_tests_status', 'qa_security_tests_status', 'qa_api_tests_status',
                'qa_anonymisation_tests_status', 'qa_upgrade_tests_status')

    def _update_meta_qa_rating(self):
        return self._update_any_rating('meta_qa_rating', 'qa_applicable', LOW_MED_HIGH_RATING,
                                       ComponentVersionModel.get_quality_assurance_fields())

    def _get_profile_must_fields(self):
        ret = ['owner_maintainer', 'owner_responsible_qa', 'owner_product_manager', 'owner_program_manager',
                'owner_escalation_list', 'owner_expert', 'owner_architect',
                'dev_language', 'dev_raml', 'dev_repo', 'dev_issuetracker_component', 'dev_docs', 'dev_api_is_public']

        if self.qa_applicable:
            ret += list(ComponentVersionModel.get_quality_assurance_fields())

        return ret

    def _field_is_filled(self, field):
        d = model_to_dict(self)
        return 0 if d[field] in ("unknown", "", None, "?") else 1

    def update_rating(self):
        completeness = 0
        max_completeness = 0
        not_filled_fields = []

        for f in self._get_profile_must_fields():
            if self._field_is_filled(f):
                completeness += 1
            else:
                not_filled_fields.append("Summary: " + f)
            max_completeness += 1

        max_requirements_count, not_filled_requirements, not_signed_requirements = self.get_requirements_status()
        completeness += max_requirements_count - len(not_filled_requirements)
        max_completeness += max_requirements_count
        not_filled_fields += not_filled_requirements

        if self.qa_applicable:
            max_qa_rating = len(ComponentVersionModel.get_quality_assurance_fields()) * max(LOW_MED_HIGH_RATING.values())
            qa_rating = self.meta_qa_rating * max_qa_rating / 100.0
        else:
            max_qa_rating = 0
            qa_rating = 0

        if (max_qa_rating + max_requirements_count) > 0:
            self.meta_rating = int(100 * (max_requirements_count - len(not_signed_requirements) + float(qa_rating)) / (max_qa_rating + max_requirements_count))
        else:
            self.meta_rating = 100

        if max_completeness:
            self.meta_profile_completeness = int(100 * float(completeness) / max_completeness)
        else:
            self.meta_profile_completeness = 100

        self.meta_profile_not_filled_fields = ", ".join(sorted(not_filled_fields))
        self.meta_profile_not_signed_requirements = ", ".join(sorted(not_signed_requirements))
        self._update_meta_qa_rating()

        super().save()

    def get_requirements_status(self, requirement_set_id=None):
        requirement_sets = []

        if requirement_set_id:
            requirement_sets.append(requirement_set_id)
        else:
            for r in RequirementSet.objects.all():
                requirement_sets.append(r.id)

        max_requirements_count = 0
        not_filled_fields = []
        not_signed_requirements = []

        owner_requirements = RequirementStatusEntry.objects.all().filter(component_version_id=self.id, type__id=REQ_OWNER_STATUS)
        signee_requirements = RequirementStatusEntry.objects.all().filter(component_version_id=self.id, type__id=REQ_SIGNEE_STATUS)

        for set_id in requirement_sets:
            if self.excluded_requirement_set.filter(id=set_id).exists():
                continue

            max_requirements_count += RequirementSet.objects.get(pk=set_id).requirements.count()

            for req in owner_requirements:
                if req.requirement.sets.filter(id=set_id).exists():
                    if req.status.id in (None, REQ_STATUS_UNKNOWN):
                        not_filled_fields.append(str(req.requirement))

            for req in signee_requirements:
                if req.requirement.sets.filter(id=set_id).exists():
                    if req.status.id != REQ_STATUS_READY:
                        not_signed_requirements.append(str(req.requirement))

        return max_requirements_count, not_filled_fields, not_signed_requirements

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

    def delete_with_dependencies(self):
        # Clearing the many-to-many relationships
        self.depends_on.clear()

        # Once all many-to-many links are cleared, delete the object itself
        self.delete()

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        self.update_meta_locations_and_product_versions()
        self.update_rating()
        super().save()

    class Meta:
        ordering = ['-version']
        permissions = [
            ("experts_change", "Component Experts can to change"),
            ("experts_delete", "Component Experts can to delete"),
            ("qa_change", "QA responsible an to change"),
            ("qa_delete", "QA responsible an to delete"),
            ("program_manager_change", "Can program manager to change"),
            ("program_manager_delete", "Can program manager to delete"),
            ("product_manager_change", "Can product manager to change"),
            ("product_manager_delete", "Can product manager to delete"),
            ("escalation_list_change", "Can persons in escalation list to change"),
            ("escalation_list_delete", "Can persons in escalation list to delete"),
            ("architect_change", "Can architect to change"),
            ("architect_delete", "Can architect to delete"),
        ]

    def __str__(self):
        return "%s - %s" % (self.component.name, self.version)


class ComponentDependencyModel(models.Model):
    type = models.CharField(max_length=16, choices=DEPENDENCY_TYPE, default=DEPENDENCY_TYPE[0][0],
                            help_text=
                            "Compile time - Given component requires the other component statically and can't be compiled w/o it; "
                            "Strong - component can't operate w/o the other being deployed and running; "
                            "Weak - component require the other to unblock certain functionality, however still can work well w/o it; "
                            "R/W - component reads data from the other OR modify state of another component; "
                            "R/O - component reads data from the other, BUT doesn't modify state of another component; "
                            "W/O - component doesn't get any data from the other, BUT can modify it's state;")

    component = models.ForeignKey(ComponentModel, on_delete=models.CASCADE)
    version = models.ForeignKey(ComponentVersionModel, on_delete=models.CASCADE)
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
                                          on_delete=models.CASCADE)
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


class JiraIssue(django_atlassian.models.djira.Issue):
    def save(self, *args, **kwargs):
        return

    def delete(self, *args, **kwargs):
        return


class Credential(models.Model):
    name = models.CharField(max_length=64, primary_key=True, unique=True)
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    description = models.CharField(max_length=512, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class ExternalService(models.Model):
    name = models.CharField(max_length=64)
    link = models.CharField(
        max_length=2048,
        blank=True,
        null=True,
        help_text="Link to service for example " "http://example.com",
    )
    ignore_ssl = models.BooleanField(verbose_name="Ignore SSL certificate")
    credentials = models.ForeignKey( 
        Credential, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Service - {self.name}"


class DocType(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.name}"


class DocLink(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    type = models.ForeignKey(DocType, on_delete=models.CASCADE)
    url = models.URLField(max_length=2048, help_text="Url for document")
    component_version = models.ForeignKey(
        ComponentVersionModel, on_delete=models.CASCADE, related_name="document_links"
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        unique_together = ['type', 'url', 'component_version']


class ComponentWidget(models.Model):
    widget = models.CharField(max_length=32, unique=True)
    show_for_all_release_family = models.BooleanField(default=False,
                                                      help_text='This flag overrides options selected '
                                                                'in release family field')
    release_family = models.ManyToManyField(ProductFamilyModel, blank=True,
                                            help_text='Show widget for components under these release families.')


class StaticLinksCategoryModel(models.Model):
    name = models.CharField(max_length=64, unique=True, help_text="Name of category", null=False, blank=False)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class StaticLinksModel(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text="Name of link", null=False, blank=False)
    url = models.URLField(max_length=2048, null=False, blank=False)
    category = models.ForeignKey(StaticLinksCategoryModel, null=True, blank=True, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='static_links', null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.image:
            new_image = self.reduce_image_size(self.image)
            self.image = new_image
        super().save(*args, **kwargs)

    @staticmethod
    def reduce_image_size(image):
        img = Image.open(image)
        old_size = img.size
        new_size = (1024, 768)
        if old_size > new_size:
            img.thumbnail(new_size, Image.LANCZOS)
        thumb_io = BytesIO()
        img.save(thumb_io, format='webp', quality=99)
        new_image = File(thumb_io, name=f'{image.name.split(".")[0]}.webp')
        return new_image

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
