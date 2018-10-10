from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.conf import settings

import json, re

from annotator.models import Document, Annotation

class BaseStorageView(View):
	def dispatch(self, request, *args, **kwargs):
		# All PUT/POST requests must contain a JSON body. We decode that here and
		# interpolate the value into the view argument list.
		if request.method in ('PUT', 'POST'):
			if not re.match("application/json(; charset=UTF-8)?", request.META['CONTENT_TYPE'], re.I):
				return HttpResponseBadRequest("Request must have application/json content type.")
				
			try:
				body = json.loads(request.body.decode("utf8"))
			except:
				 return HttpResponseBadRequest("Request body is not JSON.")
				 
			if not isinstance(body, dict):
				return HttpResponseBadRequest("Request body is not a JSON object.")
			
			# Interpolate the parsed JSON body into the arg list.
			args = [body] + list(args)

		# All requets return JSON on success, or some other HttpResponse.
		try:
			ret = super(BaseStorageView, self).dispatch(request, *args, **kwargs)
			
			if isinstance(ret, HttpResponse):
				return ret
				
			# DELETE requests, when successful, return a 204 NO CONTENT.
			if request.method == 'DELETE':
				return HttpResponse(status=204)
				
			ret = json.dumps(ret)
			resp = HttpResponse(ret, mimetype="application/json")
			resp["Content-Length"] = len(ret)
			return resp
		except ValueError as e:
			return HttpResponseBadRequest(str(e))
		except PermissionDenied as e:
			return HttpResponseForbidden(str(e))
		except ObjectDoesNotExist as e:
			return HttpResponseNotFound(str(e))
		except Exception as e:
			if settings.DEBUG: raise # when debugging, don't trap
			return HttpResponseServerError(str(e))
			
		return ret

class Root(BaseStorageView):
	http_method_names = ['get']
	
	def get(self, request):
		return {
			"name": "Django Annotator Store",
			"version": "0.0.1",
		}
	
class Index(BaseStorageView):
	http_method_names = ['get', 'post']
	
	def get(self, request):
		# index. Returns ALL annotation objects. Seems kind of not scalable.
		return Annotation.as_list()
	
	def post(self, request, client_data):
		# create. Creates an annotation object and returns a 303.
		obj = Annotation()
		obj.owner = request.user if request.user.is_authenticated() else None
		try:
			obj.document = Document.objects.get(id=client_data.get("document"))
		except:
			raise ValueError("Invalid or missing 'document' value passed in annotation data.")
		obj.set_guid()
		obj.data = "{ }"
		obj.update_from_json(client_data)
		obj.save()
		return obj.as_json(request.user) # Spec wants redirect but warns of browser bugs, so return the object.

class Annot(BaseStorageView):
	http_method_names = ['get', 'put', 'delete']
	
	def get(self, request, guid):
		# read. Returns the annotation.
		obj = Annotation.objects.get(guid=guid) # exception caught by base view
		return obj.as_json(request.user)
	
	def put(self, request, client_data, guid):
		# update. Updates the annotation.
		obj = Annotation.objects.get(guid=guid) # exception caught by base view
		
		if not obj.can_edit(request.user):
			raise PermissionDenied("You do not have permission to modify someone else's annotation.")
		
		obj.update_from_json(client_data)
		obj.save()
		return obj.as_json(request.user) # Spec wants redirect but warns of browser bugs, so return the object.
		
	def delete(self, request, guid):
		obj = Annotation.objects.get(guid=guid) # exception caught by base view
		
		if not obj.can_edit(request.user):
			raise PermissionDenied("You do not have permission to delete someone else's annotation.")
		
		obj.delete()
		return None # response handled by the base view

class Search(BaseStorageView):
	http_method_names = ['get']
	def get(self, request):
		try:
			document = Document.objects.get(id=request.GET.get("document"))
		except:
			raise ValueError("Invalid or missing 'document' value passed in the query string.")
		qs = Annotation.objects.filter(document=document)
		return {
			"total": qs.count(),
			"rows": Annotation.as_list(qs=qs, user=request.user)
		}
		
class EditorView(TemplateView):
	template_name = 'annotator/editor.html'
	def get_context_data(self, **kwargs):
		context = super(EditorView, self).get_context_data(**kwargs)
		context['storage_api_base_url'] = reverse('annotator.root')[0:-1] # chop off trailing slash 
		context['document'] = get_object_or_404(Document, id=kwargs['doc_id'])
		return context

