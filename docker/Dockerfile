FROM debian:bookworm
RUN apt update -y
RUN apt upgrade -y
RUN apt install python3-pip python3-full nginx supervisor -y
WORKDIR /code

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
COPY ./docker/uwsgi/uwsgi.ini /code/
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /var/log/nginx
RUN mkdir -p /var/log/uwsgi

RUN ln -sf /code/docker/nginx/household-nginx.conf /etc/nginx/sites-enabled/household-nginx.conf
RUN ln -sf /code/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN python manage.py collectstatic --noinput
CMD ["/usr/bin/supervisord", "-n"]