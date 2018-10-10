from django.db import models
from django.utils import timezone

class Ward(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    pub_date = models.DateTimeField('Date entered', default=timezone.now)

class Anc(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    ward = models.ForeignKey('Ward', on_delete=models.CASCADE)
    ## boundries = models.
    pub_date = models.DateTimeField('Date entered', default=timezone.now)

class Smd(models.Model):
    id = models.CharField(max_length=4, primary_key=True)
    anc = models.ForeignKey('Anc', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Date entered', default=timezone.now)

class Commissioner(models.Model):
    commissioner_name = models.CharField(max_length=20, primary_key=True, help_text='First and last name of the commissioner of this ANC')
    anc = models.ForeignKey('Anc', on_delete=models.CASCADE)
    active = models.BooleanField('Active status of commissioner')
