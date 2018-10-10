# TODO: split this into base, develop, and release images

FROM python:3
RUN apt-get update && apt-get install -y wget libpq-dev libxml2 libxslt1.1 libxml2-dev libxslt1-dev python-libxml2 python-libxslt1 libyaml-dev
COPY . /srv/app
WORKDIR /srv/app
RUN pip install -r requirements.txt
RUN pip install uwsgi
RUN wget -O /srv/app/static/ancs.json http://ancfinder.org/static/ancs.json && wget -O /srv/app/static/meetings.json http://ancfinder.org/static/meetings.json

RUN python3 manage.py syncdb --noinput
RUN python3 manage.py collectstatic --noinput

EXPOSE 8000

# Run these when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
CMD ["/usr/local/bin/uwsgi", "--ini", "uwsgi.ini"]
