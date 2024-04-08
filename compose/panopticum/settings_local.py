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

# ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost']
# CSRF_TRUSTED_ORIGINS = ['http://0.0.0.0', 'http://127.0.0.1', 'http://localhost']
