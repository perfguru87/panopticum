# Panopticum
Software services registry for IT, RnD, DevOps, Support, Maintenance, Documentation and Operations teams. Could be used to document and link all your Kubernetes services together before and after they go live.

![Panopticum](https://worksthatwork.com/assets/Articles/81/Images/NYC2.jpg)

Inspired by ["Persistent Fabric"](https://translate.google.com/translate?hl=en&sl=auto&tl=en&u=https%3A%2F%2Fhabr.com%2Fru%2Fcompany%2Foleg-bunin%2Fblog%2F462937%2F) (c) Avito and ["Panopticon"](https://en.wikipedia.org/wiki/Panopticon)

# Features

- Components registry
- Components attributes: category, language, framework, maintainers, etc.
- Components dependencies
- Other connected objects: Products, Persons, 
- REST API

# Todo

HIGH PRIO
- Reflect applied filters in URL to let direct links work
- Component details page
- Product/Branch and Location class filter support
- Product must have only one component version linked when admin saves component version
- Show 100 rows by default and increase scale by: 25, 100, 500, all

MED PRIO
- Integration with Active Directory: user auth
- Integration with Active Directory: people and org chart syncup
- Roles: allow users to manage only their components (QA manages QA fields, Dev - manage dev fields, etc)
- Export whole data to XLS
- Component data completeness column (like 0-100%, where 100% is when all 'mandatory' fields initialized)
- Add missed fields
- Embed static documentation page
- Add endpoints (URL to component mapping)
- Custom documentation links: type, title, link

LOW PRIO
- Export components dependency graph (all, selected components)
- Components diagram (all, selected components)
- Integration with ADN (auto documentation)
- Custom attributes/tags on components and search
- Integrate with git repo: scan libraries dependencies in source code
- Integrate with publically available product build system: propogate component version and link it with Product version

## Requirements

- Python3.0+
- Django2.0+

## Installation
### Install python3

CentOS-7:
```
sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum -y install python36u
sudo yum -y install python36u-pip
sudo yum -y install openssl-devel
sudo yum -y install python36u-devel
export PYCURL_SSL_LIBRARY=openssl
export LDFLAGS=-L/usr/local/opt/openssl/lib;export CPPFLAGS=-I/usr/local/opt/openssl/include;
sudo pip3.6 install pycurl
```

MacOS:

Install [Mac port](https://www.macports.org/install.php) first

Then:
```
sudo port install openssl
export PYCURL_SSL_LIBRARY=openssl
export LDFLAGS=-L/usr/local/opt/openssl/lib;export CPPFLAGS=-I/usr/local/opt/openssl/include;
sudo port install py36-psycopg2
pip3.6 install pycurl
```

### Install Django and other requirements

```
sudo pip3.6 install -r requirements.txt
```

### Install WSGI

https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/uwsgi/

CentOS-7:
```
yum -y install uwsgi uwsgi-plugin-python3
```

### Connecting to a database
By default django uses the sqlite database, but you can define the connection to your database in the panopticum_django/settings_local.py file:
```
cat >> panopticum_django/settings_local.py << EOD
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pt',
        'USER': 'pt',
        'PASSWORD': 'my secret password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
EOD
```

NOTE: please refere to Django [documentation](https://docs.djangoproject.com/en/2.1/ref/databases/) to see which databases are supported. For example Django 2.1 supports PosgtreSQL-9.4 and higher so it will not work on default CentOS-7 which has PostgreSQL-9.2 out of the box

### Create DB schema (apply migrations)
```
python3.6 ./manage.py migrate
```

### Create Django admin panel superuser

```
python3.6 ./manage.py createsuperuser
```

### Authenticate via Active Directory
In order to use AD `settings_local.py` should contain the following:
```python3.7
import ldap
from django_auth_ldap.config import LDAPSearch

AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"
AUTH_LDAP_BIND_DN = "username"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
                        "ou=users,dc=example,dc=com",
                        ldap.SCOPE_SUBTREE,
                        "(uid=%(user)s)")
```
For more information please refer to [documentation](https://django-auth-ldap.readthedocs.io/en/latest/authentication.html).

## Running the server

```
python3.6 ./manage.py runserver 0.0.0.0:8000
