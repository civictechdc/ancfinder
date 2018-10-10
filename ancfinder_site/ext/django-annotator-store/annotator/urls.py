from django.conf.urls import patterns, url

from annotator.views import Root, Index, Annot, Search, EditorView

urlpatterns = patterns('',
	# storage API
    url(r'^/$', Root.as_view(), name='annotator.root'),
    url(r'^/annotations$', Index.as_view(), name='annotator.index'),
    url(r'^/annotations/([\w\-]+)$', Annot.as_view(), name='annotator.annotation'),
    url(r'^/search$', Search.as_view(), name='annotation.search'),
    
    # public pages
    url(r'^/document/(?P<doc_id>[\w\-]+)/edit$', EditorView.as_view(), name='annotation.editor'),
)

