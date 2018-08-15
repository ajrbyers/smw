FROM python:2.7-alpine3.6

ENV DATABASE_HOST=Null
ENV DATABASE_NAME=rua
ENV DATABASE_USER=rua
ENV DATABASE_PASS=pass
ENV DJANGO_SETTINGS_MODULE=core.settings_dev
ENV PYTHONPATH=/rua/src
ENV TEST_ENVIRONMENT=True

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
        mariadb-dev && \
    rm -rf /var/cache/apk/* && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h && \
    mkdir /rua && \
    mkdir -p /usr/lib/readline && \
    mkdir -p /run/nginx && \
    mkdir -p /var/log/gunicorn && \
    mkdir -p /var/log/nginx && \
    ln -s /usr/lib/libreadline.a /usr/lib/readline/libreadline.a && \
    ln -s /usr/lib/libhistory.a /usr/lib/readline/libhistory.a

COPY ./src /app
COPY ./docker/supervisord.conf /etc/supervisord/supervisord.conf
# .git directory required by raven versoning package
COPY ./.git/ /.git/
COPY ./requirements.txt /requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /requirements.txt && \
    pip install gunicorn

RUN python /app/manage.py collectstatic --noinput

WORKDIR /app

ENTRYPOINT ["supervisord", "-c", "/etc/supervisord/supervisord.conf"]
