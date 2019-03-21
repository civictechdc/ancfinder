FROM python:3.7.0

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

# create working directory and move our app there
WORKDIR /srv
COPY requirements.txt /srv/requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8000

VOLUME /srv/app
VOLUME /srv/static
