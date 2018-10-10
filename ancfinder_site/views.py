from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
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
	}
