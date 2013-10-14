from django.shortcuts import render
from django.http import Http404, HttpResponse
import datetime, collections

try:
	import json
except ImportError:
	import simplejson as json

anc_data_as_json = open("ancbrigadesite/static/ancs.json").read()
anc_data = json.loads(anc_data_as_json, object_pairs_hook=collections.OrderedDict)

def TemplateContextProcessor(request):
	return {
		"ancs": anc_data,
	}

def home(request):
	return render(request, 'ancbrigadesite/index.html', { 'anc_data': anc_data_as_json } )

def anc_info(request, anc):
	anc = anc.upper()
	info = anc_data[anc[0]]["ancs"][anc[1]]
	
	prep_hoods(info, True)
	for smd in info["smds"].values():
		prep_hoods(smd, False)
		
	info["census"]["H0050001_PCT"] = { "value": int(round(100.0 * info["census"]["H0050001"]["value"] / info["census"]["H0040001"]["value"])) }
	info["census"]["B07001_001E_PCT"] = { "value": int(round(100.0 * (info["census"]["B07001_065E"]["value"] + info["census"]["B07001_081E"]["value"]) / info["census"]["B07001_001E"]["value"])) }

	return render(request, 'ancbrigadesite/anc.html', {'anc': anc, 'info': info})
	
def about(request):
	return render(request, 'ancbrigadesite/about.html')

def share(request):
	return render(request, 'ancbrigadesite/share.html')

def authority(request):
	return render(request, 'ancbrigadesite/authority.html')
	
def elections(request):
	return render(request, 'ancbrigadesite/elections.html')

def bigmap(request):
	return render(request, 'ancbrigadesite/map.html', { 'anc_data': anc_data_as_json } )

def legal(request):
	return render(request, 'ancbrigadesite/legal.html')
	
def prep_hoods(info, is_anc):
	def is_part(h):
		if h.get("part-of-neighborhood", 0) < (.9 if is_anc else .6): return "parts of "
		return ""
		
	# First sort by population and remove the smallest neighborhood intersections
	# so long as the cumulative population removed is less than 5% of the total
	# population. These are either degenerate intersections of very small area or
	# non-residential neighborhoods like the Tidal Basin or Union Station.
	hoods = list(info["neighborhoods"])
	hoods.sort(key = lambda h : h["population"])
	p = 0
	pt = sum(h["population"] for h in hoods)
	while True:
		p += hoods[0]["population"]
		if p > .05*pt: break
		hoods.pop(0)
	
	# Sort neighborhoods by putting the ones that are "entirely" contained in this
	# ANC/SMD first, and then sort by population.
	hoods.sort(key = lambda h : (is_part(h), -h["population"]))

	# If there are more than six neighborhoods, remove ones from the end and replace with
	# "and other areas".
	if len(hoods) > 6:
		hoods = hoods[0:6]
		hoods.append({ "name": "other areas" })

	# For a nice string for display.
	hoods = [is_part(h) + h["name"] for h in hoods]
	if len(hoods) <= 2:
		hoods = " and ".join(hoods)
	else:
		hoods[-1] = "and " + hoods[-1]
		hoods = ", ".join(hoods)
		
	info["neighborhood_list"] = hoods
	
