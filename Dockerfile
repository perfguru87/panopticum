FROM python:3.6-alpine
WORKDIR /whl
RUN apk add alpine-sdk
RUN pip wheel gevent psycopg2 -w /whl

FROM python:3.6-alpine
WORKDIR /usr/src/app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY --from=0 /whl /whl
COPY ./requirements.txt .
RUN pip install /whl/*.whl && pip install -r requirements.txt
COPY . .
CMD gunicorn panopticum_django.wsgi:application --bind 0.0.0.0:8000 -k gevent
