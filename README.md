Table of Contents
=================

   * [Summary](#summary)
   * [Panopticum Philosophy](#panopticum-philosophy)
   * [Workflow](#workflow)
      * [Data Model](#data-model)
      * [Initial data seeding](#initial-data-seeding)
      * [Regular workflow:](#regular-workflow)
   * [Features](#features)
   * [Todo](#todo)
      * [Requirements](#requirements)
      * [Installation](#installation)
         * [Install PostgreSQL](#install-postgresql)
         * [Install python3](#install-python3)
         * [Install Django and other requirements](#install-django-and-other-requirements)
         * [Install WSGI](#install-wsgi)
         * [Connecting to a database](#connecting-to-a-database)
         * [Configuring JIRA account](#configuring-jira-account)
         * [Create DB schema (apply migrations)](#create-db-schema-apply-migrations)
         * [Create Django admin panel superuser](#create-django-admin-panel-superuser)
         * [Authenticate via Active Directory](#authenticate-via-active-directory)
      * [Running the server](#running-the-server)
      * [Running at docker-compose](#running-at-docker-compose)
      * [Active Directory users import](#active-directory-users-import)
      * [Data model visualization](#data-model-visualization)
      
# Summary
Software services registry for IT, RnD, DevOps, Support, Maintenance, Documentation and Operations teams. It could be used to document and link all your microservices together before and after they go live.

![Panopticum](https://worksthatwork.com/assets/Articles/81/Images/NYC2.jpg)

Inspired by ["Persistent Fabric"](https://translate.google.com/translate?hl=en&sl=auto&tl=en&u=https%3A%2F%2Fhabr.com%2Fru%2Fcompany%2Foleg-bunin%2Fblog%2F462937%2F) (c) Avito and ["Panopticon"](https://en.wikipedia.org/wiki/Panopticon)

UI is based on ["django-gentelella"](https://github.com/GiriB/django-gentelella)

![Component info example](https://github.com/perfguru87/panopticum/raw/master/panopticum/static/images/panopticum-component.png)

# Panopticum Philosophy

Modern large cloud systems typically have so-called [microservices](https://martinfowler.com/articles/microservices.html) 
architecture, when every service is responsible for a specific set of functionality like account and user management, orders
processing, web store, audit, etc. This microservices architecture helps to structure and simplify development,
deployment, operation and maintenance of large systems when alternative `monolith` approach becomes
[inefficient](https://martinfowler.com/bliki/MicroservicePremium.html)

When a system becomes really large and number or services grows you have to deal with organizational challenges
(like [Conway's law](https://en.wikipedia.org/wiki/Conway%27s_law)) and eventually fall
into the concept when a development team is fully responsible for a service, including design, development, testing, deployment, maintenance and even operation (['You built it, you own it'](https://dl.acm.org/doi/pdf/10.1145/1142055.1142065?download=true) (C) Amazon 2006.)

However, the more developers you have in your organization and the more microservices you run, the quicker you realize that some common aspects of service behavior like performance, security, maintainability, etc require additional focus, skill set and even mandatory review procedures to minimize the number of production incidents.

The 'Panopcitum' philosophy is based on approach when you have your RnD organization built from two types of teams:

1. `Vertical` teams - regular development teams that are responsible for the end to end delivery and knowledge of
owned components including functionality, design, features set, etc. These teams are in charge of all the phases
of ['Software Development Lifecycle'](https://en.wikipedia.org/wiki/Systems_development_life_cycle) phases like
work estimation, component design, code and tests development, testing, roll-out and maintenance. 

2. `Horizontal` teams - a set of `experts'` teams to help `vertical` development teams to deal with complicated areas like
overall system architecture, performance, security, quality assurance, documentation, operations, maintenance, etc by
sharing best practices, providing tools, establishing design and implementation review process, etc.

![Panopticum in Software Development Lifecycle](https://github.com/perfguru87/panopticum/raw/master/panopticum/static/images/panopticum-sdlc.png)

Working together with `vertical` development teams, `experts` accumulate specific knowledge and share it across all 
the development teams to help them to reduce the number of problems in production.

`Panopticum` helps both `developers` and `experts` to observe the overall landscape and status of all the components
in the system. Also it helps `experts` to maintain a set of standard recomendations (like every component must have 
unit tests, performance test, troubleshooting guide, etc) and even define mandatory sign-off procedure before a
component goes to production. Ironically, components are treated as `prisoners` and experts teams as `jailers` and so `panopticum` plays a role of centralized place to see all the bad and good guys. :-)

# Workflow

### Data Model

Panopticum database objects and their relations:

![Component data model](https://github.com/perfguru87/panopticum/raw/master/panopticum/static/images/panopticum-model.png)

Key components' attributes:
- `Category` - a way to group similar components, like: platform, data services, applications, virtual infrastructure, etc.
- `Data privacy class` - represents what kind of data a component is managing: customer data, customer secrets, metadata, etc
- `Location class` - different components can be deployed in different locations: datacenter, on-prem, customer PC, mobile phone, etc

### Initial data seeding

1. Import users from Active Directory (or create them manually)
2. Create requirements groups and requirements in the admin panel
3. Fill-in standard models like: Component Data Privacy class, Category, Vendors, etc 
4. Import initial set of microservices, their attributes and relations using Excel import function

[TODO example]

### Regular workflow: 

4. Component owners add new components or update information about a component in the admin panel
5. Experts' teams' leaders sign-off requirements before a component goes public
6. Product Managers and RnD unit managers monitor overall status and plan the resources accordingly

# Features

- Components registry: category, language, framework, maintainers, dependencies, etc
- Component requirements management and sign-off: autotests, operational, compliance, maintainability, etc
- Users sync-up from Active Directory (maintaners, product managers, QA experts)
- REST API

# Todo

HIGH PRIO
- Component tags, search by components tags in dashboard
- URL to components dashboard with selected menu items
- Property change audit (author and time of every property change)
- Component data change history widget (who changed what, like in JIRA)
- Roles: allow users to manage only their components (QA manages QA fields, Dev - manage dev fields, etc)
- Export whole data to XLS
- Embed static documentation page
- Add endpoints (URL to component mapping)
- New field: service is highly loaded
- Component 'dependee'

MED PRIO
- New release approval checklist
- People - work hours
- People - vacations
- Libraries dependencies
- Multiple languages/frameworks per component
- Tooltip (hint) with possible component life state: legacy, new, mature, ...
- Tooltip (hint) with possible component data accesss: Data, Metadata only, ...
- Chart with all type of issues from JIRA (not just bugs)

LOW PRIO
- External links validation
- Integration with git: number of commits per last weeks
- Integration with git: number of contributors per last weeks
- Integration with git: overall activity
- Integration with JIRA: number of bugs per last weeks/months
- Integration with JIRA: number of open bugs, tasks
- Dashboard with components dependency graph (all, selected components)
- Components diagram (all, selected components)
- Integration with Confluence (auto documentation)
- Custom attributes/tags on components and search
- Integrate with git repo: scan libraries dependencies in source code
- Integrate with build systems: propogate component version and link it with Product version
- True Single-page-application
- Correlation map between component rating and number of bugs in production
- Link to language docs
- Org chart browser
- Git repos branches browser

## Requirements

- Python3.7+
- Django3.1+

## Installation

### Install PostgreSQL
This step is optional, you can choose whatever DB you prefer for Django

```
sudo rpm -Uvh https://yum.postgresql.org/11/redhat/rhel-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
sudo yum -y install postgresql11-server postgresql11-contrib
sudo /usr/pgsql-11/bin/postgresql-11-setup initdb
sudo systemctl enable postgresql-11
sudo systemctl start postgresql-11
sudo -u postgres psql
postgres=# create database panopticum;
postgres=# create user panopticum with encrypted password 'my secret password';
postgres=# grant all privileges on database panopticum to panopticum;
sudo echo "host all all 127.0.0.1/32 md5" > /var/lib/pgsql/11/data/pg_hba.conf
sudo systemctl restart postgresql-11
```

### Install python3

CentOS-7:
```
sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum -y install python36
sudo yum -y install python36-pip
sudo yum -y install python36-psycopg2

```

MacOS:

Install [Mac port](https://www.macports.org/install.php) first

Then:
```
sudo port install py36-psycopg2
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
        'NAME': 'panopticum',
        'USER': 'panopticum',
        'PASSWORD': 'my secret password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
TIME_ZONE = 'Europe/Sofia'
PAGE_TITLE = 'My Components Registry'
EOD
```

NOTE: please refere to Django [documentation](https://docs.djangoproject.com/en/2.1/ref/databases/) to see which databases are supported. For example Django 2.1 supports PosgtreSQL-9.4 and higher so it will not work on default CentOS-7 which has PostgreSQL-9.2 out of the box

### Configuring JIRA account
In order to support JIRA issues detection in notes/comments and highligh them with tooltips you can configure

```
cat >> panopticum_django/settings_local.py << EOD
JIRA_CONFIG = {
    'URL': 'https://jira.mycompany.com/',
    'USER': 'panopticum',
    'PASSWORD': 'my secret password'
}
```

### Create DB schema (apply migrations)
```
python3 ./manage.py migrate
```

### Create Django admin panel superuser

```
python3 ./manage.py createsuperuser
```

### Load initial fixtures

```
DJANGO_SETTINGS_MODULE=panopticum_django.settings PYTHONPATH=. django-admin loaddata init.json
```

### Authenticate via Active Directory
In order to use AD `settings_local.py` should contain the following:
```python
import ldap
from django_auth_ldap.config import LDAPSearch

AUTH_LDAP_SERVER_URI = "ldap://ldap.example.com"
AUTH_LDAP_BIND_DN = "username"
AUTH_LDAP_BIND_PASSWORD = "password"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
                        "ou=users,dc=example,dc=com",
                        ldap.SCOPE_SUBTREE,
                        "(uid=%(user)s)")

AUTHENTICATION_BACKENDS = ["panopticum.ldap.PanopticumLDAPBackend",
                           "django.contrib.auth.backends.ModelBackend"]


AUTH_LDAP_USER_FLAGS_BY_GROUP = {
     "is_active": "cn=active,ou=users,dc=example,dc=com",
     "is_staff": "cn=staff,ou=users,dc=example,dc=com",
     "is_superuser": "cn=superuser,ou=users,dc=example,dc=com"
}

# django user model and ldap fields map
AUTH_LDAP_USER_ATTR_MAP = {
    "dn": "distinguishedName",
    "first_name": "givenname",
    "last_name": "sn",
    "email": "mail",
    "title": "title",
    "mobile_phone": "mobile",
    "office_phone": "telephoneNumber",
    "info": "info",
    "employee_number": "employeeNumber",
    "active_directory_guid": "objectGUID",
    #"hidden": "msExchHideFromAddressLists"
}

# Object relation map for adding foreign key objects like AUTH_LDAP_USER_ATTR_MAP.
# key is foreignKey field at django model
# value is LDAP field
AUTH_LDAP_FOREIGNKEY_USER_ATTR_MAP = {
    "organization": "company",
    "photo": "thumbnailphoto",
    "department": "department",
    "manager": {
        "searchField": "dn",
        "ldapFieldName": "manager"
    }
}
```
For more information please refer to [documentation](https://django-auth-ldap.readthedocs.io/en/latest/authentication.html).

## Running the server

```
python3 ./manage.py runserver 0.0.0.0:8000
```

## Running at docker-compose

```bash
pip install docker-compose
docker-compose up -d
```

Service will available at http://127.0.0.1:8080/

## Active Directory users import

For import users from your Active Directory use:

```
python3  manage.py ad-sync
```

## Data model visualization

```
python3 manage.py graph_models -a -g -o model.png
```
