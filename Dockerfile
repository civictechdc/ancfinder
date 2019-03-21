FROM codefordc2/ancfinder-base:1.0

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

# create working directory and move our app there
WORKDIR /srv/app
COPY . /srv/app

# set environment Vars
ENV DJANGO_ENV=test
ENV STATIC_ROOT=/srv/app/static

# create a space for our static static
# collectstatic below will copy files to this location
VOLUME /srv/app/static

# expose port and start app
EXPOSE 8000
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python manage.py collectstatic --noinput
CMD ["uwsgi", "--ini", "/srv/app/uwsgi.ini"]
