from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import MultipleObjectsReturned
import json

from panopticum.models import *


class DomainUsersParser:
    def __init__(self):
        self.filename = None

    def usage(self):
        print(r"Usage: ", file=sys.stderr)
        print(r"# pip install ldapdomaindump", file=sys.stderr)
        print(r"# ldapdomaindump -o /tmp/ -u \"DOMAIN\USER\" ldap://LDAP.SERVER.URL:PORT", file=sys.stderr)
        print(r"# python ./manage.py ad-sync /tmp/domain_users.json", file=sys.stderr)

    def init(self, filenames):
        if len(filenames) != 1:
            self.usage()
            return False
        self.filename = filenames[0]

    def _get(self, json_data, key, default=None):
        if key not in json_data:
            if default is None:
                raise RuntimeError("Can't find '%s' property in:\n%s" % (key, json.dumps(json_data, indent=2)))
            return default

        v = json_data[key]
        if type(v) == list:
            return ", ".join([str(val) for val in v])
        elif type(v) == dict:
            return v
        return str(v)

    def _alloc_obj_by_name(self, class_name, json_data, key):
        name = self._get(json_data, key, default="")
        if name:
            try:
                return class_name.objects.get(name=name)
            except class_name.DoesNotExist as e:
                obj = class_name(name=name)
                obj.save()
                return obj
        else:
            return None

    def sync(self):
        skipped = 0
        created = 0
        updated = 0
        warnings = 0

        with open(self.filename) as json_file:
            data = json.load(json_file)
            for user_data in data:
                a = self._get(user_data, 'attributes')

                email = self._get(a, 'mail', "")
                principal_name = self._get(a, 'userPrincipalName', "")
                if email == "":
                    email = principal_name

                if email is "":
                    print("Skip user: %s" % (self._get(a, 'name')))
                    skipped += 1
                    continue

                email = email.lower()
                employee_number = self._get(a, 'employeeNumber', "")
                guid = self._get(a, 'objectGUID')
                name = self._get(a, 'displayName', "")

                obj = None
                if employee_number:
                    try:
                        obj = Person.objects.get(employee_number=employee_number)
                    except Person.DoesNotExist as e:
                        pass

                if obj is None and guid:
                    try:
                        obj = Person.objects.get(active_directory_guid=guid)
                    except Person.DoesNotExist as e:
                        pass

                if obj is None and email:
                    try:
                        obj = Person.objects.get(email=email)
                    except Person.DoesNotExist as e:
                        pass
                    except MultipleObjectsReturned as e:
                        print("warning: multiple users with email: %s" % email)

                if obj is None and name:
                    try:
                        obj = Person.objects.get(name=name)
                    except Person.DoesNotExist as e:
                        pass

                if obj is None:
                    obj = Person(name=name, email=email, active_directory_guid=guid, employee_number=employee_number)
                    created += 1
                else:
                    updated += 1

                obj.country = self._alloc_obj_by_name(Country, a, 'co')
                obj.organization = self._alloc_obj_by_name(Organization, a, 'company')
                obj.org_department = self._alloc_obj_by_name(Department, a, 'department')

                obj.email = email
                obj.employee_number = employee_number
                obj.active_directory_guid = guid

                obj.name = name if name else email
                obj.title = self._get(a, 'title', "")
                obj.location = self._get(a, 'l', "")
                obj.info = self._get(a, 'info', "")
                obj.mobile_phone = self._get(a, 'mobile', "")
                obj.office_phone = self._get(a, 'telephoneNumber', "")
                obj.hidden = self._get(a, 'msExchHideFromAddressLists', "") != ""

                print("%s user: %s" % ("Update" if obj.id else "Create", obj.email.encode('utf-8').strip()))
                obj.save()

            print("-" * 80)
            print("Created: %d" % created)
            print("Updated: %d" % updated)
            print("Skipped: %d" % skipped)
            print("Warnings: %d" % warnings)


class Command(BaseCommand):
    def handle(self, **options):
        print(options)

        p = DomainUsersParser()
        try:
            p.init(options['domain_users'])
            p.sync()
        except RuntimeError as err:
            raise CommandError(err)

    def add_arguments(self, parser):
        parser.add_argument('domain_users', nargs='+', help='a path to the domain_users.json file generated by ldapdomaindump', type=str)
