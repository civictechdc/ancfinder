from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from ancbrigadesite.models import Document
from ancbrigadesite.views import anc_data

import re

def is_valid_anc(value):
	if not re.match("^[0-9][A-Z]$", value):
		raise ValidationError("An ANC is a number followed by an uppercase letter.")
	if value[0] not in anc_data or value[1] not in anc_data[value[0]]['ancs']:
		raise ValidationError("%s is not an ANC." % value)

class UploadDocumentForm(forms.Form):
	anc = forms.CharField(
		label="ANC",
		max_length=2,
		initial="9X",
		validators=[is_valid_anc],
		help_text="Enter the ANC number, like 3B, that this document is associated with.",
		widget=forms.TextInput(attrs={'class':'input-large'})
		)
	
	docfile = forms.FileField(
		label='File',
		help_text='Select the document to upload.'
		)

@permission_required('ancbrigadesite.add_document')
def upload_document(request):
	# Handle file upload
	if request.method == 'POST':
		form = UploadDocumentForm(request.POST, request.FILES)
		if form.is_valid():
			newdoc = Document()
			newdoc.anc=form.cleaned_data['anc']
			newdoc.set_document_content(request.FILES['docfile'])
			newdoc.save()

			# Redirect to the document list after POST
			return HttpResponseRedirect(reverse('ancbrigadesite.backend_views.edit_document', args=[newdoc.id]))
	else:
		form = UploadDocumentForm() # A empty, unbound form

	return render_to_response(
		'ancbrigadesite/upload_document.html',
		{ 'form': form },
		context_instance=RequestContext(request)
	)

@permission_required('ancbrigadesite.change_document')
def edit_document(request, doc_id):
	class EditDocumentForm(forms.ModelForm):
		class Meta:
			model = Document

	doc = get_object_or_404(Document, id=doc_id)

	if request.method == "POST":
		form = EditDocumentForm(request.POST, instance=doc)
		if form.is_valid():
			# Save and redirect back to page.
			doc.save()
			return HttpResponseRedirect(reverse('ancbrigadesite.backend_views.edit_document', args=[doc.id]))
	else:
		form = EditDocumentForm(instance=doc)
		
	# Make sure the document is ready for annotation.
	doc.populate_annotation_document()

	return render_to_response(
		'ancbrigadesite/edit_document.html',
		{
			'document': doc,
			'form': form,
			'storage_api_base_url':reverse('annotator.root')[0:-1], # chop off trailing slash 
		},
		context_instance=RequestContext(request)
	)

