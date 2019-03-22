from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
import logging
import requests
import json
import urllib 
from django.http import JsonResponse

from ancfinder_site.models import *

logger = logging.getLogger(__name__)

# Class based templates
class HomeTemplateView(TemplateView):
	template_name = 'ancfindersite/index.html'

class AboutTemplateView(TemplateView):
	template_name = 'ancfindersite/about.html'

class WhatAreAncsTemplateView(TemplateView):
	template_name = 'ancfindersite/what_are_ancs.html'

class ExploreAncs(TemplateView):
	template_name = 'ancfindersite/explore_ancs.html'

# Defines context for template
def TemplateContextProcessor(request):
	# For master.html's Explore menu, we need the list of ancs
	# by ward.
	import collections
	ancs_by_ward = collections.defaultdict(list)
	anc_list = []

	# #retrieve all wards from database
    # wards = Ward.objects.all()
	# for current_ward in wards:
	# 	#retrieve all ancs for that ward
	# 	#logger.info("ward: " + current_ward.id)
	# 	ancs = Anc.objects.filter(ward=current_ward.id)
	# 	for current_anc in ancs:
	# 		#associate ancs with ward
	# 		ancs_by_ward[current_ward.id].append(current_anc.id)
	# 		anc_list.append(current_anc.id)


	return {
		"MAPBOX_API_KEY": settings.MAPBOX_API_KEY,
	}


def fetch_anc_data(request, *args, **kwards):
	r = requests.get('https://opendata.arcgis.com/datasets/fcfbf29074e549d8aff9b9c708179291_1.geojson')
	r.raise_for_status()
	return JsonResponse(r.json())


def location_search(request, *args, **kwargs):
	body_data = {}
	if request.META.get('CONTENT_TYPE', '').lower() == 'application/json' and len(request.body) > 0:
		try:
			body_data = json.loads(request.body)
		except Exception as e:
			return HttpResponseBadRequest(json.dumps({'error': 'Invalid request: {0}'.format(str(e))}), content_type="application/json")
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	str_address = body['strAddress']
	r = requests.post('http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx/findLocation2', data={'f':'json', 'str': str_address})
	r.raise_for_status()
	
	return JsonResponse(r.json())

def post(self,request, *args, **kwargs):
    if self.request.is_ajax():
        return self.ajax(request)

def ajax(self, request):
	logger.info("ajax request received...")
	response_dict = {'success': True}
	action = request.POST.get('action','')

	if(action == 'get_anc_bounds'):
		anc_id = request.POST.get('id','')
		logger.info("requestion anc " + anc_id)

	if(hasattr(self, action)):
		response_dict = getattr(self, action)(request)
		anc = Anc.objects.get(id='anc_id')
		response_dict = {'boundries': anc.boundries}

	return HttpResponse(simplejson.dumps(response_dict), mimetype='application/json')
