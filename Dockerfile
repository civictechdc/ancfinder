# TODO: split this into base, develop, and release images
### This file defines the ancfinder container

FROM python:3.6.4
WORKDIR /srv/app
COPY . /srv/app
RUN pip install -r requirements.txt
EXPOSE 8000

# Ensure that the model and database are correctly mapped
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate

# Run these when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
