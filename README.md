# Household Planner

The household planner is a web application built for planning todos and similar for shared living spaces, specifically. Although it can also be used for single households.

## Setup

First setup a Python venv:
```
# Set up venv
python -m venv env
# Activate venv
# Linux/Mac
source ./env/bin/activate
# Windows
.\env\bin\activate.bat
# or
.\env\bin\activate.ps1
```

Running this requires a few dependencies. These can be installed as follows:
```
# Installing requirements
python -m pip install -r requirements.txt
```

Before the first execution the database has to be set up:
```sh
# Build migrations for the current app
python manage.py makemigrations

# Run the migrations
python manage.py migrate
```

Afterwards the application can be run using the following:
```sh
python manage.py runserver <port>
```

## Access to the admin panel

A superuser to access the admin panel can be created as follows:
```sh
python manage.py createsuperuser
```