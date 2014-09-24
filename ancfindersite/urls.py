from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import *

admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', HomeTemplateView.as_view(), name='ancfindersite_home',),
    url(r'^about$', AboutTemplateView.as_view(), name='ancfindersite_about',),
    url(r'^about/update-anc$', ANCUpdateView.as_view(), name='anc_update_form'),
    url(r'^about/update-smd$', SMDUpdateView.as_view(), name='smd_update_form'),
    url(r'^share$', ShareTemplateView.as_view(), name='ancfindersite_share',),
    url(r'^authority$', AuthorityTemplateView.as_view(), name='ancfindersite_authority',),
    url(r'^map$', BigMapTemplateView.as_view(), name='ancfindersite_bigmap',),
    url(r'^legal$', LegalTemplateView.as_view(), name='ancfindersite_legal',),
    url(r'^(?P<anc>[0-9][A-Za-z])$', AncInfoTemplateView.as_view(), name = 'ancfindersite_anc_info'),
    url(r'^document/(?P<anc>..)/(?P<date>....-..-..)/(?P<id>\d+)(?P<slug>/.*)?$', DocumentTemplateView.as_view(), name = 'ancfindersite_document',),
    url(r'^feeds/ancfinder(?:-(\d[a-z]))?.rss$', make_anc_feed),
    url(r'^feeds/ancfinder(?:-(\d[a-z]))?.ics$', make_anc_ical),


    # Django admin
    url(r'^admin/', include(admin.site.urls)),

    # Backend
    url(r'^upload-document$', 'ancfindersite.backend_views.upload_document'),
    url(r'^document/(\d+)/edit$', 'ancfindersite.backend_views.edit_document'),
    url(r'^document-annotations', include('annotator.urls')),

    # Externals
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^emailverif/', include('emailverification.urls')),
    url(r'^registration/', include('registration.urls')),
    url(r'^accounts/login/?$', 'registration.views.loginform'),
    url(r'^accounts/logout/?$', 'registration.views.logoutview'),
    url(r'^accounts/profile/?$', 'registration.views.profile'),

    # Examples:
    # url(r'^$', 'ancfindersite.views.home', name='home'),
    # url(r'^ancfindersite/', include('ancpage.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
