import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('DB_NAME', 'panopticum_db'),
        'USER': os.environ.get('DB_USER', 'panopticum_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'panopticum_password'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432')
    }
}

TIME_ZONE = 'Europe/Sofia'
PAGE_TITLE = 'My Components Registry'
