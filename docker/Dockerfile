FROM python:3.7-alpine

RUN apk update && \
    apk -U upgrade && \
    apk add \
        gcc \
        musl-dev \
        jpeg-dev \
        gcc-avr \
        g++ \
        bash \
        libxml2-dev \
        libxslt-dev \
        readline-dev \
        python-dev \
        linux-headers \
        ncurses-dev \
        patch \
        libffi-dev \
        openssh-client \
        supervisor \
        postgresql-dev && \
    rm -rf /var/cache/apk/* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    mkdir /rua && \
    mkdir -p /usr/lib/readline && \
    mkdir -p /run/nginx && \
    mkdir -p /var/log/nginx && \
    ln -s /usr/lib/libreadline.a /usr/lib/readline/libreadline.a && \
    ln -s /usr/lib/libhistory.a /usr/lib/readline/libhistory.a

COPY ./src /app
COPY ./docker/supervisord.conf /etc/supervisord/supervisord.conf
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /app/requirements.txt && \
    pip install gunicorn

WORKDIR /app

ENV PYTHONPATH=/app

ENV DJANGO_SETTINGS_MODULE=core.settings

ENV TECH_EMAIL=tech@ubiquitypress.com

ENV DATABASE_HOST=Null
ENV DATABASE_NAME=rua
ENV DATABASE_USER=rua
ENV DATABASE_PASS=pass

ENV REDIS_HOST=127.0.0.1
ENV REDIS_PORT=6379

ENV SENTRY_DSN='https://fake:dsn@sentry.ubiquity.press/5'

ENV ORCID_API_URL='http://pub.orcid.org/v1.2_rc7/'
ENV ORCID_REDIRECT_URI='http://localhost:8002/login/orcid/'
ENV ORCID_TOKEN_URL='https://pub.orcid.org/oauth/token'
ENV ORCID_CLIENT_SECRET='fake-orcid-client-secret'
ENV ORCID_CLIENT_ID='fake-orcid-client-id'

ENV AWS_ACCESS_KEY_ID='fake-access-key-id'
ENV AWS_SECRET_ACCESS_KEY='fake-secret-access-key'
ENV AWS_STORAGE_BUCKET_NAME='service-rua'

ENV EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
ENV EMAIL_USE_TLS="True"
ENV EMAIL_HOST='smtp.mailgun.org'
ENV EMAIL_HOST_USER='fake@email-host.user'
ENV EMAIL_HOST_PASSWORD='fake-email-host-password'
ENV EMAIL_PORT="587"


ENTRYPOINT ["supervisord", "-c", "/etc/supervisord/supervisord.conf"]
