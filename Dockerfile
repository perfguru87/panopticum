FROM python:3.11-alpine
WORKDIR /whl
RUN apk update && apk upgrade
RUN apk --no-cache add alpine-sdk postgresql-dev graphviz-dev openldap-dev jpeg-dev zlib-dev git
RUN pip wheel gevent psycopg2-binary pygraphviz python-ldap pillow -w /whl

FROM python:3.11-alpine
WORKDIR /opt/panopticum
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY --from=0 /whl /whl
COPY ./requirements.txt .
RUN apk update && apk upgrade
RUN apk add openldap jpeg zlib libpq git gcc musl-dev libc-dev libffi-dev
RUN pip install /whl/*.whl && pip install -r requirements.txt
RUN pip install --upgrade -r requirements.txt
COPY . .
CMD python manage.py migrate  && gunicorn panopticum_django.wsgi:application --bind 0.0.0.0:8000 -k gevent
