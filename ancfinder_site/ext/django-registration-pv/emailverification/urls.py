from django.conf.urls import *

urlpatterns = patterns('',
    (r'^code/([0-9A-Z]+)$', 'emailverification.views.processcode'),
    (r'^code/delete/([0-9A-Z]+)$', 'emailverification.views.killcode'),
    (r'^ping/([a-zA-Z]+)$', 'emailverification.views.emailping'),
)

