FROM base:latest

WORKDIR /code

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate
RUN python manage.py createsuperuser --username $DJANGO_SUPERUSER_USERNAME --noinput