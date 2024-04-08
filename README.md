Table of Contents
=================

   * [Summary](#summary)
   * [Panopticum Philosophy](#panopticum-philosophy)
   * [Panopticum Overview](#panopticum-overview)
      * [Data model](#data-model)
      * [Usage scenario](#usage-scenario)
      * [Features](#features)
   * [Installation](#installation)
      * [Option #1 - Using docker](#option-1---using-docker)
      * [Option #2 - Manual installation](#option-2---manual-installation)
   * [Tools](#installation)
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

# Panopticum overview

## Data model

Panopticum database objects and their relations:

![Component data model](https://github.com/perfguru87/panopticum/raw/master/panopticum/static/images/panopticum-model.png)

Key components' attributes:
- `Category` - a way to group similar components, like: platform, data services, applications, virtual infrastructure, etc.
- `Data privacy class` - represents what kind of data a component is managing: customer data, customer secrets, metadata, etc
- `Location class` - different components can be deployed in different locations: datacenter, on-prem, customer PC, mobile phone, etc

## Usage scenario

Initial data seeding:

1. Create requirements groups and requirements in the admin panel
2. Fill-in standard models like: Frameworks, Languages, Component Data Privacy class, Category, Vendors, etc 
3. Import users from Active Directory (or create them manually)
4. Import initial set of microservices, their attributes and relations using Excel import function

Once components list is created:

5. Component owners can add new components or update information about a component in the admin panel
6. Experts' teams' leaders can review the requirements completion and sign-off components

## Features

Current features:

- Components registry: category, language, framework, maintainers, dependencies, etc
- Component requirements management and sign-off: autotests, operational, compliance, maintainability, etc
- Users sync-up from Active Directory (maintaners, product managers, QA experts)
- Tech Radar (inspired by [Zalando Tech Radar](https://github.com/zalando/tech-radar))
- REST API

Possible upcoming features ideas:

HIGH PRIO
- Component tags, search by components tags in dashboard
- URL to components dashboard with selected menu items
- Property change audit (author and time of every property change)
- Component data change history widget (who changed what, like in JIRA)
- Roles: allow users to manage only their components (QA manages QA fields, Dev - manage dev fields, etc)
- Export to XLS
- Embed static documentation page
- Add endpoints (URL to component mapping)
- New field: service is highly loaded

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

# Installation

The key requirements are:

- Python3.7+
- Django4.0+

## Option #1 - Using docker

### Installing the Docker

#### Ubuntu 22.04

```bash
sudo apt update
sudo apt install -u libsasl2-dev libldap2-dev libssl-dev
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo apt install -y python3-pip
sudo pip3 install docker-compose docker==6.1.3
```

#### CentOS 9

```bash
sudo dnf update
sudo dnf remove docker
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
sudo dnf install -y python3-pip
sudo pip3 install docker-compose docker==6.1.3
```

#### Mac OS

See docker [instruction](https://docs.docker.com/desktop/install/mac-install/)
Also, you have to install python-pip and then:

```bash
pip3 install docker-compose
```

### Configuring settings & credentials (optional)

You can update credentials and settings in:
```bash
./compose/panopticum/settings_local.py
./compose/nginx/nginx-server.conf
```

For local debug only purposes you can enable 0.0.0.0 and 127.0.0.1 as allowed hosts in the `./compose/panopticum/settings_local.py`
file by uncommenting the following lines:

```bash
ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost']
CSRF_TRUSTED_ORIGINS = ['http://0.0.0.0', 'http://127.0.0.1', 'http://localhost']
```

### Preparing the static content

You have to prepare all the static files to be available for Panopticum and it's admin panel:

```bash
pip3 install -r requirements.txt
python3 manage.py collectstatic --no-input --clear
```

### Staring the Panopticum service

```bash
docker-compose up -d
```

Service will be available at http://127.0.0.1:80/

### Creating initial data

By default, Panopticum starts with empty database and has no any admin users, so you may want to create some:

```bash
docker-compose run --rm web python manage.py createsuperuser
```

After the superuser creation you have to initialize some initial content:
```bash
docker-compose run --rm web python manage.py loaddata demo.json  # use 'minimal.json' instead of 'demo' to load bare minimum content 
```

### Updating the Panopticum version

As any other Django application Panopticum requires database schema to be updated when a new version released:

```bash
docker-compose stop web
docker-compose build web
docker-compose up -d
```

## Option #2 - Manual installation

Manual installation can be useful if you want to debug or change the source code

### Installing a Database

You can choose whatever DB you prefer for Django, so here is just an example for PostgreSQL

CentOS-7:

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
sudo echo "host all all 127.0.0.1/32 md5" >> /var/lib/pgsql/11/data/pg_hba.conf
sudo systemctl restart postgresql-11
```

CentOS-9:

```
sudo yum install postgresq-server postgresql-contrib
sudo /usr/bin/postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql
postgres=# create database panopticum;
postgres=# create user panopticum with encrypted password 'my secret password';
postgres=# grant all privileges on database panopticum to panopticum;
sudo echo "host all all 127.0.0.1/32 md5" >> /var/lib/pgsql/data/pg_hba.conf
sudo systemctl restart postgresql
```

### Installing python3 modules

CentOS-7:
```
sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum -y install python36 python36-pip python36-devel
```

CentOS-9:
```
sudo yum -y install python3-pip python3-devel openldap-devel
```

MacOS:

No specific python3 installation steps required, since it should be already on your system

### Installing Django and other requirements

```
sudo pip3 install -r requirements.txt
```

### Installing WSGI

https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/uwsgi/

CentOS-7:
```
yum -y install uwsgi uwsgi-plugin-python3
```

CentOS-9
```
pip3 install uwsgi
```

### Connecting to a database

By default, django uses the SQLite database, but you can define the connection to your database in the panopticum_django/settings_local.py file:
```
cat >> panopticum_django/settings_local.py << EOD
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'panopticum_db',
        'USER': 'panopticum_user',
        'PASSWORD': 'panopticum_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
TIME_ZONE = 'Europe/Sofia'
PAGE_TITLE = 'My Components Registry'
EOD
```

NOTE: please refer to Django [documentation](https://docs.djangoproject.com/en/3.1/ref/databases/) to see which databases are supported.

### Configuring JIRA integration (optional)

In order to support JIRA issues detection in notes/comments and highlighting them with tooltips you can configure appropriate environment variables:

    JIRA_URL=
    JIRA_USER=
    JIRA_PASSWORD=

### Create DB schema (apply migrations)
```
python3 ./manage.py migrate
```

### Create Django admin panel superuser
```
python3 ./manage.py createsuperuser
```

### Load initial fixtures

It is required to load some default pre-created types and data from fixtures:

```
python3 ./manage.py loaddata demo.json  # 'demo.json' is used for initial review and evaluation, one can use 'minimal.json' for production as well
```

### Integration with Active Directory

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

### Running the server
```
python3 ./manage.py runserver 0.0.0.0:8000
```

# Tools

## Active Directory users import

For import users from your Active Directory use:

```
python3 ./manage.py ad-sync
```

## Data model visualization

```
python3 ./manage.py graph_models -a -g -o model.png
```
