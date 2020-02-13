from django.utils import timezone
import csv
import json
import logging
import re
import sys
import traceback
from enum import Enum

from django.core import serializers
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand, CommandError
from panopticum.models import *
from iso3166 import countries


class DataException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


# Provides all the utility functions in static form

class Status(Enum):
    UPDATED = 1
    CREATED = 2
    FAILED = -1


class Utility:
    comp_categories = \
        {'Category1': {'description': '', 'order': 1}}

    comp_subcategories = \
        [{'name': 'SubCategory_A', 'description': '', 'category': 'Category1'},
         {'name': 'SubCategory_B', 'description': '', 'category': 'Category1'},
         {'name': 'SubCategory_C', 'description': '', 'category': 'Category2'},
         {'name': 'SubCategory_B', 'description': '',
          'category': 'Category2'}]  # We can have duplicate SubCategory names

    comp_dataprivacies = \
        {'Framework': {'order': 1},
         'Infrastructure': {'order': 2}}  # Order can be same across records.

    comp_runtimes = ['Component', 'Driver']

    loggers = {'Logf'}

    data_centers = \
        {'USA 1': {'info': '', 'grafana': 'https://grafana.company.com/display/USA1.html',
                   'metrics': 'https://intranet.company.com/metrics/USA1.html'},
         'Europe 1': {'info': 'https://intranet.company.com/DCs/EU1.html',
                      'grafana': 'https://grafana.company.com/display/EU1.html',
                      'metrics': 'https://intranet.company.com/metrics/EU1.html'}}

    db_vendors = ['MSSQL', 'None']

    depl_envs = {"-": "Not Applicable", "K8S": "K8S pod"}

    # We could have called this as deployment type. It basically tells where this component belongs
    depl_locations = {
        'aws': {'name': 'Amazon Web Services', 'description': 'https://aws.amazon.com/', 'order': 1},
        'cloud-agent': {'name': 'Cloud agent unit', 'description': 'Agent application that works with cloud datacenter',
                        'order': 2},
        'cloud': {'name': 'Cloud datacenter', 'description': '', 'order': 3},
        'azure': {'name': 'Microsoft Azure', 'description': 'https://azure.microsoft.com/en-us/', 'order': 4}
    }

    # depl_location_mapping = \
    #     {'cloud-only': 'Cloud datacenter',
    #      'cloud-agent': 'Cloud agent unit',
    #      'cloud': 'Cloud datacenter',
    #      'PDS operator side': 'On-prem Partner',
    #      'on-prem': 'On-prem centralized',
    #      'on-prem-only': 'On-prem centralized',
    #      'azure': 'Microsoft Azure',
    #      'aws': 'Amazon Web Services',
    #      'plesk': 'Plesk',
    #      'Agent': 'On-prem agent unit',
    #      'TBD': 'TBD'
    #      }

    langs = {'Go-lang', 'Python', 'C/C++', 'Javascript', 'Java', 'Ruby', 'Erlang', 'shellscript', 'Perl',
             'Objective-C', 'Android', 'Powershell-script', '.Net', 'PHP'}

    app_vendors = {'Acronis', 'OpenSource', 'Percona', 'Google', 'Commerical'}

    app_frameworks = \
        {'tornado': 'Python', 'sqlalchmey': 'Python', 'fastcgi': 'Python', 'storedprocs': 'Python',
         'aiohttp': 'Python', 'angular4': 'Javascript', 'vuejs': 'Javascript', 'angular1': 'Javascript',
         'laravel': 'PHP', 'werkzeug': 'Python', 'flask': 'Python', 'go-std': 'Go-lang',
         'beego': 'Go-lang', 'xorm': 'Go-lang', 'gorm': 'Go-lang', 'WPF': '.Net', 'angular2': 'Javascript',
         'extjs4': 'Javascript', 'gevent': 'Python', 'ruby on rails': 'Ruby', 'android sdk': 'Android',
         'wix': 'C/C++', 'phantomjs': 'Python', 'asyncio': 'Python', 'go-micro': 'Go-lang',
         'gin': 'Go-lang', 'gorp': 'Go-lang', 'DBIx': 'Perl', 'Mason': 'Perl', 'boost': 'C/C++'}

    prod_versions = {
        'Company Cloud 1.0': {'shortname': 'ComCloud1.0', 'order': 1, 'family': 'Cloud Services'},
        'Google Maps 1.0': {'shortname': 'Maps1.0', 'order': 2, 'family': 'Cloud Services'}}

    prod_families = {'Cloud Services', 'Native Applications'}

    ports = \
        {'HTTP-80': {'port': 80}, 'HTTPS-443': {'port': 443}, 'HTTP-8080': {'port': 8080}}

    # TBD: How to make sure these ones stay valid with respective seed values.
    default_depl_env = 'K8S pod'
    default_location_shortname = 'cloud'
    default_location_name = 'Cloud datacenter'
    default_prod_version = 'My Cloud Product 1.0'
    default_prod_family = 'Cloud Services'
    default_port = 'HTTPS-443'
    default_runtime = 'Component'
    default_app_vendor = 'OpenSource'
    default_dep_type = 'sync_rw'
    default_privacy = 'Application'
    default_comp_version = '2.0'
    parser = None

    @staticmethod
    def register_parser(p):
        Utility.parser = p

    @staticmethod
    def usage():
        Utility.parser.print_help()

    @staticmethod
    def alloc_obj_by_name(class_name, name: str, **kwargs):
        """ Creates record in DB if one doesn't exists. If all well, returns created object or raises an exception """
        if name is not None and name.strip() is not "":
            name = name.strip()
            try:
                obj, created = \
                    class_name.objects \
                        .filter(name__iexact=name) \
                        .get_or_create(name=name,
                                       defaults=kwargs)
                if created is True:
                    logging.info("Created record with name [%s] for model [%s]", name, class_name)
                return obj

            except MultipleObjectsReturned as e:
                obj = list(class_name.objects.filter(name__iexact=name))[0]
                logging.error('Received 2 objects for class [%s] and name [%s]. Returning first object from the list',
                              class_name,
                              name)
                return obj
            except Exception as e:
                logging.error('FATAL while creating object for class [%s], name [%s]. Exception message '
                              '- [%s]',
                              class_name.__name__, name, e)
                raise e
        else:
            logging.error('Couldn\'t get object for class [%s] and name [%s]', class_name, name)
            raise DataException('Couldn\'t get object for class {0} and name {1}'.format(class_name, name))

    @staticmethod
    def get_comp_category(name, description='', order=1):
        return Utility.alloc_obj_by_name(ComponentCategoryModel, name,
                                         description=description, order=order)

    @staticmethod
    def seed_comp_categories():
        for (name, values) in Utility.comp_categories.items():
            try:
                Utility.get_comp_category(name, description=values['description'], order=values['order'])
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_comp_subcategory(name, category_id, description=''):
        sub_category_obj = None
        created = False
        try:
            sub_category_obj, created = ComponentSubcategoryModel.objects \
                .get_or_create(name=name,
                               category_id=category_id,
                               defaults={'description': description})
        except Exception as e:
            logging.error('Ignoring exception %s', e)

        if created is True:  # We can now safely create the missing object
            logging.info("Created in model [%s] record - [%s]",
                         ComponentSubcategoryModel.__name__,
                         serializers.serialize('json', [sub_category_obj, ]))
        return sub_category_obj

    @staticmethod
    def seed_comp_subcategories():
        Utility.seed_comp_categories()  # IMP: Required step for below code to work
        for comp_subcategory in Utility.comp_subcategories:
            name = comp_subcategory['name']
            category_name = comp_subcategory['category']
            try:
                category_obj = Utility.get_comp_category(category_name)
                Utility.get_comp_subcategory(name, category_obj.id, comp_subcategory['description'])
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_comp_privacy(name, order=1):  # Creates record in DB if doesn't exists.
        return Utility.alloc_obj_by_name(ComponentDataPrivacyClassModel, name, order=order)

    @staticmethod
    def seed_comp_privacies():
        for (name, values) in Utility.comp_dataprivacies.items():
            try:
                Utility.get_comp_privacy(name, values['order'])
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_comp_runtimetypes(name, order=1):  # Creates record in DB if doesn't exists.
        return Utility.alloc_obj_by_name(ComponentRuntimeTypeModel, name, order=order)

    @staticmethod
    def seed_comp_runtimetypes():
        for name in Utility.comp_runtimes:
            try:
                Utility.get_comp_runtimetypes(name, 1)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_country(name):
        return Utility.alloc_obj_by_name(CountryModel, name)

    @staticmethod
    def seed_countries():
        for name in countries:
            try:
                Utility.get_country(name.name)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_datacenter(name, info, grafana, metrics):
        return Utility.alloc_obj_by_name(DatacenterModel, name, info=info, grafana=grafana, metrics=metrics)

    @staticmethod
    def seed_datacenters():  # TODO: Need to consider components_deployments field (M-M) data - we don't have seed
        # data yet.
        for (dc_name, dc_values) in Utility.data_centers.items():
            try:
                dbobj = Utility.get_datacenter(dc_name, dc_values['info'], dc_values['grafana'], dc_values['metrics'])
                if dbobj.grafana != dc_values['grafana'] or dbobj.metrics != dc_values['metrics'] or dbobj.info != \
                        dc_values['info']:
                    logging.info(
                        'Ignoring seed value! [%s] exists in DB with different grafana or metrics value. Seed '
                        'info value [%s], grafana value [%s], metrics value [%s].',
                        dc_name, dc_values['info'], dc_values['grafana'], dc_values['metrics'])
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, dc_name)

    @staticmethod
    def get_db_vendor(name):
        return Utility.alloc_obj_by_name(DatabaseVendorModel, name)

    @staticmethod
    def seed_db_vendors():
        for name in Utility.db_vendors:
            try:
                Utility.get_db_vendor(name)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_depl_env(name):
        return Utility.alloc_obj_by_name(DeploymentEnvironmentModel, name)

    @staticmethod
    def seed_depl_envs():
        for name, value in Utility.depl_envs.items():
            try:
                Utility.get_depl_env(value)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_depl_location(shortname, name = default_location_name, order=1, description=''):
        obj, created = \
                    DeploymentLocationClassModel.objects \
                        .filter(shortname__iexact=shortname.strip()) \
                        .get_or_create(defaults={
                                        'shortname': shortname.strip(),
                                        'name':name.strip(),
                                        'order':order,
                                        'description':description}
                        )
        if created is True:
            logging.info("Created record with name [%s] for model [%s]", name, DeploymentLocationClassModel)
        return obj

    @staticmethod
    def seed_depl_locations():
        for (shortname, dep_values) in Utility.depl_locations.items():
            try:
                dbobj = Utility.get_depl_location(shortname, name = dep_values['name'],
                                                  order=dep_values['order'], description=dep_values['description'])
                if dbobj.order != dep_values['order']:
                    logging.error('Ignoring seed value! [%s] exists in DB with different order. Seed order value [%d], '
                                 'DB order value [%d].', dep_values['name'], dep_values['order'], dbobj.order)
            except Exception as e:
                logging.error("Ignoring exception [%s] for shortname [%s], name [%s].", e, shortname, dep_values['name'])

    @staticmethod
    def get_logger(name):
        return Utility.alloc_obj_by_name(LoggerModel, name)

    @staticmethod
    def seed_loggers():
        for name in Utility.loggers:
            try:
                Utility.get_logger(name)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_lang(lang):
        return Utility.alloc_obj_by_name(ProgrammingLanguageModel, lang)

    @staticmethod
    def get_framework(framework, lang):
        return Utility.alloc_obj_by_name(FrameworkModel, framework,
                                         language_id=Utility.get_lang(lang).id)

    @staticmethod
    def seed_languages():
        for lang in Utility.langs:
            try:
                Utility.alloc_obj_by_name(ProgrammingLanguageModel, lang)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, lang)

    @staticmethod
    def seed_app_frameworks():
        for (framework, lang) in Utility.app_frameworks.items():
            try:
                lang_obj = Utility.get_lang(lang)
                frame_obj = Utility.alloc_obj_by_name(FrameworkModel, framework,
                                                      language_id=lang_obj.id)
                if frame_obj.language_id != lang_obj.id:
                    logging.info(
                        'Ignoring seed value! [%s] exists in DB with different language value. '
                        'Seed value [%d], DB value [%d].', frame_obj.name, lang_obj.id, frame_obj.language_id)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, framework)

    @staticmethod
    def seed_prod_families():
        for prod_family in Utility.prod_families:
            try:
                Utility.alloc_obj_by_name(ProductFamilyModel, prod_family)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, prod_family)

    @staticmethod
    def get_prod_family(family):
        return Utility.alloc_obj_by_name(ProductFamilyModel, family)

    @staticmethod
    def get_prod_version(prod_name, prod_shortname, family, order=1):
        product_family_obj = Utility.get_prod_family(family)
        if product_family_obj is None:
            logging.error('Could\'t get product family object. Will skip productversion [%s]',
                          prod_name)
        else:
            return Utility.alloc_obj_by_name(ProductVersionModel,
                                             prod_name,
                                             shortname=prod_shortname,
                                             order=order,
                                             family_id=product_family_obj.id)

    @staticmethod
    def seed_prod_versions():
        for (product_version_name, version_details) in Utility.prod_versions.items():
            try:
                family = version_details['family'] if version_details['family'] != '' else Utility.default_prod_family
            except KeyError:
                family = Utility.default_prod_family

            try:
                order = version_details['order'] if version_details['order'] != '' else 1
            except KeyError:
                order = 1

            try:
                Utility.get_prod_version(product_version_name,
                                         prod_shortname=version_details['shortname'],
                                         order=order,
                                         family=family)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, product_version_name)

    @staticmethod
    def get_app_vendor(name):
        return Utility.alloc_obj_by_name(SoftwareVendorModel, name)

    @staticmethod
    def seed_app_vendors():
        for name in Utility.app_vendors:
            try:
                Utility.get_app_vendor(name)
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, name)

    @staticmethod
    def get_port(port_name, port_value):
        return Utility.alloc_obj_by_name(TCPPortModel, port_name, port=port_value)

    @staticmethod
    def seed_ports():
        for (port_name, port_value) in Utility.ports.items():
            try:
                port_obj = Utility.get_port(port_name, port_value['port'])
                if port_obj.port != port_value['port']:
                    logging.debug(
                        'Ignoring seed value! [%s] exists in DB with different port value. DB value [%d] vs Seed '
                        'value [%d].', port_name.name, port_obj.port, port_value['port'])
            except Exception as e:
                logging.error("Ignoring exception [%s] for name [%s].", e, port_name)

    @staticmethod
    def get_comp(name, description, category_obj, privacy_obj, sub_category_obj,
                 vendor_obj, runtime_obj, life_status):
        return Utility.alloc_obj_by_name(ComponentModel, name,
                                         description=description,
                                         category_id=category_obj.id,
                                         data_privacy_class_id=privacy_obj.id,
                                         subcategory_id=sub_category_obj.id,
                                         vendor_id=vendor_obj.id,
                                         runtime_type_id=runtime_obj.id,
                                         life_status=life_status)

    @staticmethod
    def seed_comp(comp_name, description, category, subcategory, privacy, vendor, runtime_type,
                  life_status):
        category_obj = Utility.get_comp_category(category)
        sub_category_obj = Utility.get_comp_subcategory(subcategory, category_obj.id)
        privacy_obj = Utility.get_comp_privacy(privacy, 1)
        vendor_obj = Utility.get_app_vendor(vendor)
        runtime_obj = Utility.get_comp_runtimetypes(runtime_type)

        try:
            # Now we have all the supporting objects ready, we can create DB record
            comp_obj = Utility.get_comp(comp_name,
                                        description,
                                        category_obj,
                                        privacy_obj,
                                        sub_category_obj,
                                        vendor_obj,
                                        runtime_obj,
                                        life_status)
            if comp_obj.category.name == 'SEED':
                # Update record with provided values since it was created with default values earlier.
                # TODO: This can be optimized - see seed_comp_versions() function
                comp_obj.description = description
                comp_obj.category = category_obj
                comp_obj.data_privacy_class = privacy_obj
                comp_obj.subcategory = sub_category_obj
                comp_obj.vendor = vendor_obj
                comp_obj.runtime_type = runtime_obj
                comp_obj.life_status = life_status
                comp_obj.save()

            return comp_obj
        except Exception as e:
            logging.error("Ignoring exception [%s] for name [%s].", e, comp_name)

    @staticmethod
    def get_comp_dependency(dep_comp_obj: ComponentModel, comp_version_obj: ComponentVersionModel,
                            comp_type, notes=''):
        logging.debug('component version [%s - %s] and dependent_comp - [%s]',
                     comp_version_obj.component_id.name,
                     comp_version_obj.version,
                     dep_comp_obj.name,
                     )
        dep_obj, created = \
            ComponentDependencyModel.objects \
                .filter(component_id=dep_comp_obj.id, version_id=comp_version_obj.id) \
                .get_or_create(defaults=
            {
                'component_id': dep_comp_obj.id,
                'version_id': comp_version_obj.id,
                'type': comp_type,
                'notes': notes
            })
        # We CANNOT use Utility.alloc* function since we are trying to find using ids.
        if created is True:
            # dep_obj.save()
            logging.info("created record [%s] in [%s]", serializers.serialize('json', [dep_obj, ]), ComponentDependencyModel)
        return dep_obj

    @staticmethod
    def seed_comp_versions(version, comp_obj, **kwargs) -> Status:
        logging.debug('component version [%s - %s]',
                     comp_obj.name,
                     version)
        update = False
        try:
            timestamp = timezone.now()
            version, created = ComponentVersionListModel.objects\
                    .get_or_create(version = Utility.default_comp_version,
                                   defaults={
                                    'release_time': timestamp
                                   })

            comp_ver_obj, created = \
                ComponentVersionModel.objects \
                    .get_or_create(version=version,
                                   component_id=comp_obj.id,
                                   defaults={
                                       'comments': 'SEED',
                                       'dev_jira_component': '',
                                       'dev_build_jenkins_job': '',
                                       'meta_deleted': False,
                                       'dev_commit_link': ''
                                   })
            if comp_ver_obj.comments is None or comp_ver_obj.comments == 'SEED':
                update = True
        except ComponentVersionModel.DoesNotExist:
            comp_ver_obj = ComponentVersionModel.objects.create(version=version, component_id=comp_obj.id)
            created = True
        except ComponentVersionListModel.DoesNotExist as e:
            logging.error('FATAL Exception - [%s]', e)
            print(traceback.format_exc())
            return Status.FAILED

        if update is True or created is True:
            try:
                comp_ver_obj.comments = 'SEED'
                comp_ver_obj.dev_jira_component = ''  # dont have info
                comp_ver_obj.dev_build_jenkins_job = ''  # dont have info
                comp_ver_obj.dev_commit_link = ''  # dont have info
                comp_ver_obj.dev_api_is_public = ''  # dont have info
                comp_ver_obj.compliance_fips_notes = ''  # dont have info
                comp_ver_obj.compliance_gdpr_notes = ''  # dont have info
                comp_ver_obj.compliance_api_notes = ''  # dont have info

                # operational readiness fields
                comp_ver_obj.op_applicable = False  # dont have info
                comp_ver_obj.op_guide_status = 'unknown'  # dont have info
                comp_ver_obj.op_guide_notes = ''  # dont have info
                comp_ver_obj.op_failover_status = 'unknown'  # dont have info
                comp_ver_obj.op_failover_notes = ''  # dont have info
                comp_ver_obj.op_horizontal_scalability_status = 'unknown'  # dont have info
                comp_ver_obj.op_horizontal_scalability_notes = ''  # dont have info
                comp_ver_obj.op_scaling_guide_status = 'unknown'  # dont have info
                comp_ver_obj.op_scaling_guide_notes = ''  # dont have info
                comp_ver_obj.op_sla_guide_status = 'unknown'  # dont have info
                comp_ver_obj.op_sla_guide_notes = ''  # dont have info
                comp_ver_obj.op_metrics_status = 'unknown'  # dont have info
                comp_ver_obj.op_metrics_notes = ''  # dont have info
                comp_ver_obj.op_alerts_status = 'unknown'  # dont have info
                comp_ver_obj.op_alerts_notes = ''  # dont have info
                comp_ver_obj.op_zero_downtime_status = 'unknown'  # dont have info
                comp_ver_obj.op_zero_downtime_notes = ''  # dont have info
                comp_ver_obj.op_backup_status = 'unknown'  # dont have info
                comp_ver_obj.op_backup_notes = ''  # dont have info
                comp_ver_obj.op_safe_restart = False  # dont have info
                comp_ver_obj.op_safe_delete = False  # dont have info
                comp_ver_obj.op_safe_redeploy = False  # dont have info
                # maintainability
                comp_ver_obj.mt_http_tracing_status = 'unknown'  # dont have info
                comp_ver_obj.mt_http_tracing_notes = ''  # dont have info
                comp_ver_obj.mt_logging_completeness_status = 'unknown'  # dont have info
                comp_ver_obj.mt_logging_completeness_notes = ''  # dont have info
                comp_ver_obj.mt_logging_format_status = 'unknown'  # dont have info
                comp_ver_obj.mt_logging_format_notes = ''  # dont have info
                comp_ver_obj.mt_logging_storage_status = 'unknown'  # dont have info
                comp_ver_obj.mt_logging_storage_notes = ''  # dont have info
                comp_ver_obj.mt_logging_sanitization_status = 'unknown'  # dont have info
                comp_ver_obj.mt_logging_sanitization_notes = ''  # dont have info
                comp_ver_obj.mt_db_anonymisation_status = 'unknown'  # dont have info
                comp_ver_obj.mt_db_anonymisation_notes = ''  # dont have info
                comp_ver_obj.qa_manual_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_manual_tests_notes = ''  # dont have info
                comp_ver_obj.qa_unit_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_unit_tests_notes = ''  # dont have info
                comp_ver_obj.qa_e2e_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_e2e_tests_notes = ''  # dont have info
                comp_ver_obj.qa_perf_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_perf_tests_notes = ''  # dont have info
                comp_ver_obj.qa_longhaul_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_longhaul_tests_notes = ''  # dont have info
                comp_ver_obj.qa_security_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_security_tests_notes = ''  # dont have info
                comp_ver_obj.qa_api_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_api_tests_notes = ''  # dont have info
                comp_ver_obj.qa_anonymisation_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_anonymisation_tests_notes = ''  # dont have info
                comp_ver_obj.qa_upgrade_tests_status = 'unknown'  # dont have info
                comp_ver_obj.qa_upgrade_tests_notes = ''  # dont have info
                comp_ver_obj.meta_deleted = False  # dont have info
                comp_ver_obj.component_id = comp_obj

                maintainers = Utility.get_users_by_emailid(kwargs['owners'])
                if maintainers is not None and len(maintainers) > 0:
                    comp_ver_obj.owner_maintainer = maintainers[0]
                    for maintainer in maintainers:
                        comp_ver_obj.owner_expert.add(maintainer)
                        comp_ver_obj.owner_escalation_list.add(maintainer)

                product_managers = Utility.get_users_by_emailid(kwargs['product_managers'])
                for pm in product_managers if product_managers is not None else []:
                    comp_ver_obj.owner_product_manager.add(pm)

                architects = Utility.get_users_by_emailid(kwargs['architects'])
                for a in architects if architects is not None else []:
                    comp_ver_obj.owner_architect.add(a)

                languages = kwargs['dev_language'].split(',')
                for lang in languages:
                    if lang.strip() not in ('', 'TBD', '?', '-'):
                        comp_ver_obj.dev_language.add(
                            Utility.get_lang(lang.strip()))

                frameworks = kwargs.pop('dev_framework').split(',')
                for framework in frameworks:
                    if framework.strip() not in ('', 'TBD', '?', '-'):
                        comp_ver_obj.dev_framework.add(
                            Utility.get_framework(framework.strip(), 'TBD'))

                dbs = kwargs['dev_database'].split(',')
                for db in dbs:
                    if db.strip() not in ('', 'TBD', '?', '-'):
                        comp_ver_obj.dev_database.add(Utility.get_db_vendor(db.strip()))

                loggers = kwargs['dev_logging'].split(',')
                for logger in loggers:
                    if logger.strip() not in ('', 'TBD', '?', '-'):
                        comp_ver_obj.dev_logging.add(Utility.get_logger(logger.strip()))

                comp_ver_obj.dev_raml = kwargs['dev_raml']
                comp_ver_obj.dev_repo = kwargs['dev_repo']
                comp_ver_obj.dev_docs = kwargs['dev_docs']
                comp_ver_obj.dev_public_docs = ''
                if comp_obj.vendor is not None and comp_obj.vendor.name != Utility.default_app_vendor:
                    comp_ver_obj.dev_public_docs = comp_ver_obj.dev_docs
                    comp_ver_obj.dev_docs = ''
                comp_ver_obj.save()

                logging.info("%s record with name [%s] for model [%s]",
                             "Updated" if update is True else "Created",
                             comp_ver_obj.component_id.name,
                             ComponentVersionModel)

                # We now fill the dependencies
                for dep_name in re.sub('\*|N/A|-$', '', kwargs['dependents']).splitlines():
                    category_obj = Utility.get_comp_category('SEED')
                    # IMP: TODO: Use QuerySet and use regex to find the component.
                    # RISK with below approach is we won't find component if names are not exact.
                    # IMP: Chances are very high we create default component record in DB which may have appear
                    # later in CSV. This can be optimized by getting component record from CSV and create it first
                    try:
                        dependent_comp_obj = Utility.get_comp(dep_name.strip(),
                                                              'SEED',
                                                              category_obj,
                                                              Utility.get_comp_privacy('SEED'),
                                                              Utility.get_comp_subcategory('SEED', category_obj.id),
                                                              Utility.get_app_vendor(
                                                                  Utility.default_app_vendor),
                                                              Utility.get_comp_runtimetypes(
                                                                  Utility.default_runtime),
                                                              'unknown')

                        Utility.get_comp_dependency(dependent_comp_obj,
                                                    comp_ver_obj,
                                                    Utility.default_dep_type)
                    except Exception as e:
                        logging.error("Ignoring exception [%s] for name [%s].", e, dep_name.strip())

                # We now create Component Deployment Model.
                Utility.get_comp_deployment(kwargs['deployment_name'],  # name
                                            comp_obj.name,  # service name
                                            kwargs['binary_name'],  # binary name
                                            comp_ver_obj,  # version id
                                            kwargs['deployment_env'],  # deployment environment
                                            Utility.default_prod_version,  # product version
                                            kwargs['location_cls'],  # deployment location class
                                            kwargs['open_ports']
                                            )


                return Status.UPDATED if update is True else Status.CREATED
            except Exception as e:
                logging.error('FATAL Exception - [%s]', e)
                print(traceback.format_exc())
                return Status.FAILED

    @staticmethod
    def get_comp_deployment(name, service_name, binary_name, comp_version_obj, environment, product_version,
                            location_cls, open_ports, notes=''):
        logging.debug('component [%s] with service_name [%s]',
                     name,
                     service_name)
        prod_ver_obj = \
            Utility.get_prod_version(product_version,
                                     Utility.prod_versions[Utility.default_prod_version]['shortname'],
                                     Utility.prod_versions[Utility.default_prod_version]['family'],
                                     Utility.prod_versions[Utility.default_prod_version]['order'])

        dep_env_obj = Utility.get_depl_env(Utility.depl_envs[environment]
                                           if environment in Utility.depl_envs
                                           else Utility.default_depl_env)

        open_port_objs = []  # of type TCPPortModel
        # TODO: Below code should be along with other code where we are parsing CSV data.
        for port_entry in re.sub('TBD|-$', '', open_ports).splitlines():
            if port_entry == '':
                logging.info('port_entry is blank. Ignoring entry.')
                continue
            tmp_list = [x.strip() for x in port_entry.split(':')]
            port_name = tmp_list[0]
            if len(tmp_list) == 1:
                logging.error('port_name - [%s] doesn\'t have a port value. Ignoring entry [%s].',
                              port_name,
                              port_entry)
                continue
            value = tmp_list[1]
            for port_value in re.sub('\[|\]', '', re.sub('#.*', '', value).strip()).split(','):
                port_value = port_value.strip()
                port_name_entry = port_name + '-' + port_value
                open_port_objs.append(Utility.get_port(port_name_entry, port_value))  # TODO: Check for None objects

        # location_cls can have values like - cloud,on-prem
        locations = location_cls.split(
            ',')  # TODO: Below code should be along with other code where we are parsing CSV data.
        for location_shortnm in locations:
            if location_shortnm.strip() not in ('', '-', '?'):
                for x in Utility.depl_locations.keys():
                    # Unfortunately we can have case mismatch. Alternate way is
                    # to have Case-insensitive dict but costly to perfect and maintain.
                    if x.strip().upper() == location_shortnm.strip().upper():
                        location_shortnm = x
                        break
                tmp = Utility.depl_locations.get(location_shortnm.strip()) if location_shortnm.strip() in Utility.depl_locations.keys() else None
                if tmp is None:
                    tmp = {
                        "name" : Utility.default_location_name,
                        "order": 1,
                        "description": ""
                    }
                    location_shortnm = Utility.default_location_shortname
                # Check if component exists in DB
                comp_depl_obj, created = ComponentDeploymentModel.objects \
                    .get_or_create(name=name,
                                   service_name=service_name,
                                   component_version_id=comp_version_obj.id,
                                   environment_id=dep_env_obj.id,
                                   location_class=Utility.get_depl_location(
                                       location_shortnm,
                                       tmp['name'],
                                       tmp['order'],
                                       tmp['description']
                                   ),
                                   defaults={'service_name': service_name,
                                             'binary_name': binary_name,
                                             'notes': notes,
                                             'product_version_id': prod_ver_obj.id})

                if created is True:
                    for port_objs in open_port_objs:
                        comp_depl_obj.open_ports.add(port_objs)
                    comp_depl_obj.save()
                    logging.info("Created record with name [%s] for model [%s]", name, ComponentDeploymentModel)
    @staticmethod
    def get_str_data_from_list(row, name):
        return row[name].strip() if row[name].strip() != '' else 'TBD'

    @staticmethod
    def parse_defaults(defaults):
        with open(defaults[0]) as jsonfile:
            jsondata = json.load(jsonfile)
            Utility.comp_categories = jsondata['ComponentCategories']
            Utility.comp_subcategories = jsondata['ComponentSubCategories']
            Utility.comp_dataprivacies = jsondata['ComponentDataPrivacies']
            Utility.comp_runtimes = jsondata['ComponentRuntimes']
            Utility.loggers = jsondata['Loggers']
            # Utility.countries = jsondata['Countries']
            Utility.data_centers = jsondata['DataCenters']
            Utility.db_vendors = jsondata['DBVendors']
            Utility.depl_envs = jsondata['DeploymentEnvironments']
            # Utility.depl_env_mapping = jsondata['DeploymentEnvironmentMapping']
            Utility.depl_locations = jsondata['DeploymentLocations']
            # Utility.depl_location_mapping = jsondata['DeploymentLocationMapping']
            Utility.langs = jsondata['ProgrammingLanguages']
            Utility.app_vendors = jsondata['ApplicationVendors']
            Utility.app_frameworks = jsondata['ApplicationFrameworks']
            Utility.prod_versions = jsondata['ProductVersions']
            Utility.prod_families = jsondata['ProductFamilies']
            Utility.ports = jsondata['Ports']
            Utility.default_depl_env = jsondata['Defaults']['DeploymentEnvironment']
            Utility.default_location_shortname = jsondata['Defaults']['DeploymentLocationShortName']
            Utility.default_location_name = jsondata['Defaults']['DeploymentLocationName']
            Utility.default_prod_family = jsondata['Defaults']['ProductFamily']
            Utility.default_prod_version = jsondata['Defaults']['ProductVersion']
            Utility.default_port = jsondata['Defaults']['Port']
            Utility.default_runtime = jsondata['Defaults']['ComponentRuntime']
            Utility.default_app_vendor = jsondata['Defaults']['ApplicationVendor']
            Utility.default_dep_type = jsondata['Defaults']['DependencyType']
            Utility.default_privacy = jsondata['Defaults']['ComponentDataPrivacy']
            Utility.default_comp_version = jsondata['Defaults']['ComponentVersion']
        return True

    @staticmethod
    def get_users_by_emailid(email_ids: str):
        users = []
        for email_id in email_ids.strip().split(','):
            if not email_id.strip() in ['', 'TBD', '-']:
                try:
                    users.append(User.objects.filter(email__iexact=email_id.strip()).get())
                except Exception as e:
                    logging.error("Couldn't find user with email id [%s]. Exception [%s]", email_id, e)
                    pass
            else:
                pass

        return users


# TBD: Find out a way to fill details for below -
# DatacenterModel.components_deployments --- This has separate table datacentermodel_components_deployments

class SeedDataImporter:
    def init(self, csv_files):
        if len(csv_files) != 1:
            Utility.usage()
            return False
        self._csv_file = csv_files[0]

    def __init__(self, csv_file):
        self._csv_file = ""
        self.init(csv_file)

    @staticmethod
    def seed_simple_tables():
        Utility.seed_comp_categories()
        Utility.seed_comp_privacies()
        Utility.seed_comp_subcategories()
        Utility.seed_comp_runtimetypes()
        Utility.seed_countries()
        Utility.seed_db_vendors()
        Utility.seed_datacenters()
        Utility.seed_depl_envs()
        Utility.seed_depl_locations()
        Utility.seed_loggers()
        Utility.seed_languages()
        Utility.seed_app_frameworks()
        Utility.seed_prod_families()
        Utility.seed_prod_versions()
        Utility.seed_app_vendors()
        Utility.seed_ports()

    def parse_csv(self):
        if self._csv_file is None:
            Utility.usage()
            return False

        try:
            f = open(self._csv_file)
            f.close()
        except IOError:
            print(r"Couldn't open file %s" % self._csv_file)
            Utility.usage()
            exit(1)

        total_count: int = 0
        failed_count: int = 0
        created_count: int = 0
        updated_count: int = 0

        with open(self._csv_file, newline='') as csv_content:
            try:
                reader = csv.DictReader(csv_content)
            except csv.Error as err:
                print(r"Issues encountered reading CSV content. Make sure its valid component CSV file.")
                print(err)
                Utility.usage()
                return False

            # Seed simple DB tables (which don't have FK dependency and contents are predefined)
            SeedDataImporter.seed_simple_tables()

            try:
                for row in reader:
                    comp_name = Utility.get_str_data_from_list(row, 'Name')
                    comp_category = Utility.get_str_data_from_list(row, 'Category')
                    comp_subcategory = Utility.get_str_data_from_list(row, 'Sub-Category')
                    vendor = Utility.get_str_data_from_list(row, 'Vendor')
                    if vendor is 'TBD':
                        vendor = Utility.default_app_vendor
                    depl_container = Utility.get_str_data_from_list(row, 'Deployment Container')
                    depl_env = Utility.get_str_data_from_list(row, 'Deployment Environment')
                    if depl_env in ('-', 'N/A'):
                        depl_env = 'N/A'
                    binary_name = Utility.get_str_data_from_list(row, 'Binary name')
                    runtime_type = Utility.get_str_data_from_list(row, 'Runtime Type')
                    description = Utility.get_str_data_from_list(row, 'Description')
                    dep_str = Utility.get_str_data_from_list(row, 'Dependency')
                    dev_docs = Utility.get_str_data_from_list(row, 'Wiki')
                    if dev_docs is None:
                        dev_docs = ''
                    dev_repo = Utility.get_str_data_from_list(row, 'Repo')
                    if dev_repo is None:
                        dev_repo = ''
                    location_cls = Utility.get_str_data_from_list(row, 'Deployment Location')
                    lang_str = Utility.get_str_data_from_list(row, 'Language')
                    framwork_str = Utility.get_str_data_from_list(row, 'Framework')
                    db_str = Utility.get_str_data_from_list(row, 'DB')
                    logging_str = Utility.get_str_data_from_list(row, 'Logging')
                    dev_raml = Utility.get_str_data_from_list(row, 'REST API RAML')
                    port_str = Utility.get_str_data_from_list(row, 'Ports')
                    legacy_status = Utility.get_str_data_from_list(row, 'Is legacy?')
                    pm_str = Utility.get_str_data_from_list(row, 'PM')
                    owner_str = Utility.get_str_data_from_list(row, 'Owner')
                    architect_str = Utility.get_str_data_from_list(row, 'Architect')

                    #  Below fields are not captured in xlsx hence with default values
                    life_status = 'unknown'
                    component_obj = Utility.seed_comp(comp_name,
                                                      description=description,
                                                      category=comp_category,
                                                      subcategory=comp_subcategory,
                                                      privacy=Utility.default_privacy,
                                                      vendor=vendor,
                                                      runtime_type=runtime_type,
                                                      life_status=life_status)

                    status = Utility.seed_comp_versions(Utility.default_comp_version,
                                               component_obj,
                                               dependents=dep_str,
                                               dev_language=lang_str,
                                               dev_framework=framwork_str,
                                               dev_database=db_str,
                                               dev_logging=logging_str,
                                               dev_raml=dev_raml,
                                               dev_repo=dev_repo,
                                               dev_docs=dev_docs,
                                               open_ports=port_str,
                                               legacy_status=legacy_status,
                                               binary_name=binary_name,
                                               location_cls=location_cls,
                                               deployment_env=depl_env,
                                               deployment_name=depl_container,
                                               product_managers=pm_str,
                                               owners=owner_str,
                                               architects=architect_str)
                    if status == Status.FAILED:
                        failed_count += 1
                    elif status == Status.CREATED:
                        created_count += 1
                    elif status == Status.UPDATED:
                        updated_count += 1

                    total_count += 1
            except KeyError as e:
                logging.error('FATAL Couldn\'t find key [%s]', e)
                logging.error('Make sure you have passed valid CSV. Please check for CSV format')
                print(traceback.format_exc())
                sys.exit(-1)
            except Exception as e:
                logging.error('FATAL Exception - [%s]', e)
                print(traceback.format_exc())
                sys.exit(-1)

            # TODO: Have more stats printed like how many components created, updated, errors etc.
            print("*** Component Version record Report *** \nProcessed total [%d] record(s)\nCreated total [%d] record(s)\nUpdated total [%d] record(s)\nFailed total [%d] record(s)"
                  % (total_count,
                     created_count,
                     updated_count,
                     failed_count))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(options)
        logging.basicConfig(
            format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(funcName)s():%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO)

        if not Utility.parse_defaults(options['defaults']):
            print("[%s] cannot proceed without valid data from default.json" % args[0])
            sys.exit(-1)
        seeder = SeedDataImporter(options['seed_data'])
        try:
            seeder.parse_csv()  # Parse csv and fill up required Model instances
        except RuntimeError as err:
            Utility.usage()
            raise CommandError(err)

    def add_arguments(self, parser):
        parser.add_argument('seed_data',
                            nargs='+',
                            help='path to seeddata.csv file that you\'d generate from data collection xlsx format '
                                 'template.',
                            type=str)
        parser.add_argument('defaults',
                            nargs='+',
                            help='path to default.json file that provides required defaults which also provides '
                                 'initial seeddata.')

        Utility.register_parser(parser)
