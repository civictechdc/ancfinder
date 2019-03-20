FROM python:3.7.0

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

# create working directory and move our app there
WORKDIR /srv/app
COPY . /srv/app

# install our dependencies
RUN pip3 install -r requirements.txt

# set environment Vars
ENV DJANGO_ENV=test
ENV STATIC_ROOT=/srv/app/static

# create a space for our static static
# collectstatic below will copy files to this location
VOLUME /srv/app/static

# expose port and start app
EXPOSE 8000
