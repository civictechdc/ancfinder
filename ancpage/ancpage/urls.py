from django.conf.urls import patterns, include, url
from django.contrib import admin
from ancpage.views import home, smd_info, about, share, authority, elections

admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', home),
	url(r'^about/$', about),
	url(r'^share/$', share),
	url(r'^authority/$', authority),
	url(r'^elections/$', elections),
	url(r'^smd/(?P<smd>.{4})/$', smd_info),
	url(r'^admin/', include(admin.site.urls)),

    # Examples:
    # url(r'^$', 'ancpage.views.home', name='home'),
    # url(r'^ancpage/', include('ancpage.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
