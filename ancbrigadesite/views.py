from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
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

class HomeTemplateView(TemplateView):
	template_name = 'ancbrigadesite/index.html'
	# Override the HTTP get method to pass along anc_data to the web page
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, { 'anc_data': anc_data_as_json } )

	
class AncInfoTemplateView(TemplateView):
	template_name = 'ancbrigadesite/anc.html'
	# Override the HTTP get method to pass along some additional information
	def get(self, request, anc, *args, **kwargs):
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
			
		documents_list = ['Agenda', 'Minutes', 'Report', 'Decision', 'Draft', 'Application', 'Grant', 'Official Correspondence', 'Financial Statement', 'Operating Documents', 'Committee Agenda', 'Committee Minutes', 'Committee Report']		
		recent_docs = documents_list[:2]
		current_month = datetime.datetime.now()
		existing_documents = Document.objects.filter(anc = anc, meeting_date__month=current_month.month, meeting_date__year = current_month.year)
		

		documents = Document.objects.filter(anc=anc).order_by('-created')[0:10]
		#latest_to_upload = [ doc for doc in documents.doc_type if doc not in ]

		return render(request, self.template_name, {'anc': anc, 'current_month': current_month, 'info': info, 'rec_doc': recent_docs, 'existing_docs': existing_documents, 'documents': documents, 'census_stats': census_stats})

	

	
	
#Using Class Based Views(CBV) to implement our logic
	
class AboutTemplateView(TemplateView):
	'''This CBV generates the about page. '''
	template_name = 'ancbrigadesite/about.html'


class  ShareTemplateView(TemplateView):
	'''This CBV generates the share page. '''
	template_name = 'ancbrigadesite/share.html'


class AuthorityTemplateView(TemplateView):
	'''This CBV generates the authority page. '''
	template_name = 'ancbrigadesite/authority.html'
	
	
class  ElectionsTemplateView(TemplateView):
	'''This CBV generates the elections page. '''
	template_name =  'ancbrigadesite/elections.html'


class BigMapTemplateView(TemplateView):
	'''This CBV generates the map page. '''
	template_name = 'ancbrigadesite/map.html'
	
	#override the get method to pass anc_data to our view
	def get(self, request, *args, **kwargs):
		return render(request, self.template_name, { 'anc_data': anc_data_as_json }) 

	 
class LegalTemplateView(TemplateView):
	template_name = 'ancbrigadesite/legal.html'
	
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
	
	
# CBV for document page
class DocumentTemplateView(TemplateView):
	template_name = 'ancbrigadesite/document.html'
	def get(self, request, anc=None, date=None, id=None, slug=None, *args, **kwagrs):
		document = get_object_or_404(Document, id=id)
		return render(request, self.template_name, {"document": document})
		
		