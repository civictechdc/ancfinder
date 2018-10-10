FROM python:3.7.0

WORKDIR /srv/app

COPY ./requirements.txt /srv/app/requirements.txt
RUN pip install -r requirements.txt

COPY ./ancfinder /srv/app/ancfinder
COPY ./ancfinder_site /srv/app/ancfinder_site
COPY ./manage.py /srv/app/manage.py
COPY ./run.sh /srv/app/run.sh

RUN chmod u+x /srv/app/run.sh

VOLUME /srv/app/static

EXPOSE 8000
# Ensure that the model and database are correctly mapped
# RUN python3 manage.py makemigrations
# RUN python3 manage.py migrate

# Ensure that the model and database are correctly mapped
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

# Run these when the container launches
CMD ["./run.sh"]
