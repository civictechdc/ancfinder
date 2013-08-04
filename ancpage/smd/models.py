from django.db import models

# Create your models here.
class SMD(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    address = models.CharField(max_length=50)
    smd_telephone = models.CharField(max_length=15)
    smd_website = models.URLField()
    smd_email = models.EmailField()
    date_elected = models.DateField()
    #anc = models.ForeignKey(ANC)
    
    def __unicode__(self):
    	return u'%s %s' % (self.first_name, self.last_name)


class ANC(models.Model):
    commissioners = models.ManyToManyField(SMD)
    anc_telephone = models.CharField(max_length=15)
    anc_website = models.URLField()
    anc_email = models.EmailField()
    #next_meeting = 
    
    def __unicode__(self):
    	return u'%s %s' % (self.first_name, self.last_name)
    	
#    class Meta:
#    	ordering = ['name']