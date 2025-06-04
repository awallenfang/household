FROM debian:bookworm
RUN apt update -y
RUN apt upgrade -y
RUN apt install python3-pip python3-full nginx supervisor -y
COPY ./docker/uwsgi/uwsgi.ini /code/
COPY ./docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /var/log/nginx
RUN mkdir -p /var/log/uwsgi
RUN mkdir -p /var/log/celery

RUN ln -sf /code/docker/nginx/household-nginx.conf /etc/nginx/sites-enabled/household-nginx.conf
RUN ln -sf /code/docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord", "-n"]