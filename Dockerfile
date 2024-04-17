# Build stage
FROM python:3.11-alpine AS builder
WORKDIR /whl
RUN apk update && \
    apk --no-cache add alpine-sdk postgresql-dev graphviz-dev openldap-dev jpeg-dev zlib-dev git libpq gcc musl-dev libc-dev libffi-dev

RUN pip install --upgrade pip && \
    pip wheel gevent psycopg2-binary pygraphviz python-ldap pillow -w /whl
COPY ./requirements.txt .
RUN pip wheel -r requirements.txt -w /whl

# Final stage
FROM python:3.11-alpine
WORKDIR /opt/panopticum
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY --from=builder /whl /whl
COPY ./requirements.txt .
RUN apk update && \
    apk add --no-cache openldap jpeg zlib libpq && \ 
    pip install --upgrade pip && \
    pip install --no-cache /whl/*.whl
COPY . .
CMD python manage.py migrate  && gunicorn panopticum_django.wsgi:application --bind 0.0.0.0:8000 -k gevent