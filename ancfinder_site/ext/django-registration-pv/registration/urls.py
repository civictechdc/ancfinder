from django.conf.urls import *

urlpatterns = patterns('',
    (r'^ext/(login|associate)/start/(.+)$', 'registration.views.external_start'),
    (r'^ext/(login|associate)/return/(.+)$', 'registration.views.external_return'),
    (r'^ext/finish$', 'registration.views.external_finish'),
    (r'^reset-password$', 'registration.views.resetpassword'),
    (r'^ajax/login$', 'registration.views.ajax_login'),
    (r'^signup$', 'registration.views.new_user'),
)

