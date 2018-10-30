from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
<<<<<<< HEAD
from django.conf import settings
=======
>>>>>>> initial commit of new version of ancfinder
import logging

from ancfinder_site.models import *

logger = logging.getLogger(__name__)

# Class based templates
class HomeTemplateView(TemplateView):
	template_name = 'ancfindersite/index.html'

class AboutTemplateView(TemplateView):
	template_name = 'ancfindersite/about.html'

class WhatAreAncsTemplateView(TemplateView):
	template_name = 'ancfindersite/what_are_ancs.html'

# Defines context for template
def TemplateContextProcessor(request):
	# For master.html's Explore menu, we need the list of ancs
	# by ward.
	import collections
	ancs_by_ward = collections.defaultdict(list)
	anc_list = []

	#retrieve all wards from database
	wards = Ward.objects.all()
	for current_ward in wards:
		#retrieve all ancs for that ward
		#logger.info("ward: " + current_ward.id)
		ancs = Anc.objects.filter(ward=current_ward.id)
		for current_anc in ancs:
			#associate ancs with ward
			ancs_by_ward[current_ward.id].append(current_anc.id)
			anc_list.append(current_anc.id)


	return {
		"ancs_by_ward": sorted(ancs_by_ward.items()),
		"anc_list": sorted(anc_list),
<<<<<<< HEAD
		"MAPBOX_API_KEY": settings.MAPBOX_API_KEY,
=======
>>>>>>> initial commit of new version of ancfinder
	}

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
