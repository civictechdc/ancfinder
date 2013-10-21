from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
import datetime, collections

try:
	import json
except ImportError:
	import simplejson as json

from models import Document

anc_data_as_json = open("ancbrigadesite/static/ancs.json").read()
anc_data = json.loads(anc_data_as_json, object_pairs_hook=collections.OrderedDict)

# assemble census data on first load
def make_anc_hex_color(anc):
	def avg(t1, f1, t2, f2): return (int((t1[0]*f1+t2[0]*f2)/(f1+f2)), int((t1[1]*f1+t2[1]*f2)/(f1+f2)), int((t1[2]*f1+t2[2]*f2)/(f1+f2)))
	def hexish(tup): return "".join(("%0.2X" % d) for d in tup)
	ward_color_set = [ (27, 158, 119), (217, 95, 2), (166, 118, 29), (117, 112, 179), (231, 41, 138), (102, 166, 30), (230, 171, 2), (166, 118, 29) ]
	anc_color_set = [ (228, 26, 28), (55, 126, 184), (77, 175, 74), (152, 78, 163), (255, 127, 0), (255, 127, 0), (166, 86, 40) ]
	ward_color = ward_color_set[int(anc[0])-1]
	anc_color = anc_color_set[ord(anc[1])-ord('A')]
	return hexish(ward_color) #avg(ward_color, 1.0, anc_color, 0.22))
census_grids = { }
for ward in anc_data.values():
	for anc in ward["ancs"].values():
		for key, info in anc["census"].items():
			census_grids.setdefault(key, []).append( (anc["anc"], info["value"], make_anc_hex_color(anc["anc"])) )
for d in census_grids.values():
	d.sort(key = lambda x : x[1])

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

	census_stats = [
		{ "key": "P0180002", 	"label": "families", 		"details": "Family households" },
		{ "key": "P0180001", 	"label": "households", 		"details": "" },
		{ "key": "P0010001", 	"label": "residents", 		"details": "" },
		{ "key": "H0050001_PCT", "label": "vacant homes", 	"details": "Vacant housing units out of all housing units", "is_percent": True },
		{ "key": "B07001_001E_PCT", "label": "new residents", "details": "Residents who moved into DC in the last year", "is_percent": True },
		{ "key": "B01002_001E",	"label": "median age" },
		{ "key": "B19019_001E",	"label": "median household income", "details": "", "is_dollars": True },
		{ "key": "POP_DENSITY",	"label": "density (pop/sq-mi)", "details": "Total population divided by the area of the ANC." },
		{ "key": "liquor_licenses",	"label": "liquor licenses",	"details": "Liquor licenses held by bars and restaurants in the area" },
	]
	for s in census_stats:
		s["value"] = info["census"][s["key"]]["value"]
		s["grid"] = census_grids[s["key"]]
		
	documents = Document.objects.filter(anc=anc).order_by('-created')[0:10]

	return render(request, 'ancbrigadesite/anc.html', {'anc': anc, 'info': info, 'documents': documents, 'census_stats': census_stats})
	
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
	
def document(request, anc=None, date=None, id=None, slug=None):
	document = get_object_or_404(Document, id=id)
	return render(request, 'ancbrigadesite/document.html', { "document": document } )
