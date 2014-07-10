from django.conf.urls import patterns, include, url
from django.contrib import admin
from .views import *

admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', HomeTemplateView.as_view(), name='ancbrigadesite_home',),
	url(r'^about$', AboutTemplateView.as_view(), name='ancbrigadesite_about',),
	url(r'^share$', ShareTemplateView.as_view(), name='ancbrigadesite_share',),
	url(r'^authority$', AuthorityTemplateView.as_view(), name='ancbrigadesite_authority',),
	url(r'^map$', BigMapTemplateView.as_view(), name='ancbrigadesite_bigmap',),
	url(r'^legal$', LegalTemplateView.as_view(), name='ancbrigadesite_legal',),
	url(r'^(?P<anc>[0-9][A-Za-z])$', AncInfoTemplateView.as_view(), name = 'ancbrigadesite_anc_info'),
	url(r'^document/(?P<anc>..)/(?P<date>....-..-..)/(?P<id>\d+)(?P<slug>/.*)?$', DocumentTemplateView.as_view(), name = 'ancbrigadesite_document',),
    url(r'^feeds/ancfinder(?:-(\d[a-z]))?.rss$', make_anc_feed),
    url(r'^feeds/ancfinder(?:-(\d[a-z]))?.ics$', make_anc_ical),


	# Django admin
	url(r'^admin/', include(admin.site.urls)),

	# Backend
	url(r'^upload-document$', 'ancbrigadesite.backend_views.upload_document'),
	url(r'^document/(\d+)/edit$', 'ancbrigadesite.backend_views.edit_document'),
	url(r'^document-annotations', include('annotator.urls')),

	# Externals
	url(r'^tinymce/', include('tinymce.urls')),
	url(r'^emailverif/', include('emailverification.urls')),
	url(r'^registration/', include('registration.urls')),
    url(r'^accounts/login/?$', 'registration.views.loginform'),
    url(r'^accounts/logout/?$', 'registration.views.logoutview'),
    url(r'^accounts/profile/?$', 'registration.views.profile'),

    # Examples:
    # url(r'^$', 'ancbrigadesite.views.home', name='home'),
    # url(r'^ancbrigadesite/', include('ancpage.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
