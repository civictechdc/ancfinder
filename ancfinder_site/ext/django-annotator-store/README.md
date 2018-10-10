django-annotator-store
======================

A Django-based backend for OKF's Annotator (https://github.com/okfn/annotator).

The Annotator is a Javascript library from OKF which provides a nice UI for letting users annotate and tag arbitrary ranges in HTML content.

This project provides a Django app that is a storage backend for the Annotator.

To enable:

	Add 'annotator' to your INSTALLED_APPS in settings.py.
	
	Make sure your base.html is working. It should load jQuery >=1.7.2 and have a block called "head" in the <head/> and a block called "scripts" either later in the <head/> or at the end of the <body/>.
	
	Make sure AJAX works with CSRF protection. I enable this by adding

		<script>$('html').ajaxSend(function(event, xhr, settings) { if (!/^https?:.*/.test(settings.url)) xhr.setRequestHeader("X-CSRFToken", "{{csrf_token|escapejs}}"); });</script> <!-- {% csrf_token %} -->
		
	right after jQuery is loaded.
	
	Hook in the app to your URL space by adding `url(r'^document-annotations', include('annotator.urls')),` to your urlconf.
	
Use the Django admin to create a Document. Then browse to:

	/document-annotations/document/{id}/edit
	
where {id} is the numeric primary key of the Document you added (probably "1").

The app has a simple permissions model:

* Anyone, even anonymous users, may create annotations on any document.
* Annotations created by logged-in users can only be edited/deleted by that user or a user with the annotator.change_annotation permission (i.e. global change permission).

