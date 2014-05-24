
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
import datetime, calendar, json, collections


from models import Document, anc_data_as_json, anc_data

meeting_data = json.loads(open(settings.STATIC_ROOT + "/meetings.json").read())

# assemble census data on first load
def make_anc_hex_color(anc):
	def avg(t1, f1, t2, f2): 
		return (int((t1[0]*f1+t2[0]*f2)/(f1+f2)), int((t1[1]*f1+t2[1]*f2)/(f1+f2)), int((t1[2]*f1+t2[2]*f2)/(f1+f2)))
	
	def hexish(tup): 
		return "".join(("%0.2X" % d) for d in tup)
	
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
	
	def get_context_data(self, **kwargs):
		# Used to pass the anc_data to our home page
		context = super(HomeTemplateView, self).get_context_data(**kwargs)
		# Add in the anc_data 
		context['anc_data'] = anc_data_as_json
		return context
			
class AncInfoTemplateView(TemplateView):
	template_name = 'ancbrigadesite/anc.html'
	# Override the HTTP get method to pass along some additional information
	def get(self, request, anc, *args, **kwargs):
		anc = anc.upper()
		try:
			info = anc_data[anc[0]]["ancs"][anc[1]]
		except KeyError:
			raise Http404()
		
		# Find the next meeting and the most recent two meetings so we can
		# display related documents for those meetings.
		now = datetime.datetime.now()
		all_meetings = sorted([datetime.datetime.strptime(m, "%Y-%m-%dT%H:%M:%S")
			for m in meeting_data.get(anc, {}).get("meetings", {}).keys() ])
		next_meeting = None
		for m in all_meetings:
			if m > now:
				next_meeting = m # this is the first meeting in the future (i.e. the next meeting)
				break
		i = all_meetings.index(next_meeting) if next_meeting is not None else len(all_meetings)
		previous_meetings = all_meetings[i-2:i]

		prep_hoods(info, True)
		for smd in info["smds"].values():
			prep_hoods(smd, False)
	
		census_stats = [
			{ "key": "P0180002", 	"label": "families", 		"details": "A group of two or more related people residing together." },
			{ "key": "P0180001", 	"label": "households", 		"details": "A house, apartment, or room intended as separate living quarters." },
			{ "key": "P0010001", 	"label": "residents", 		"details": "The total population of the ANC." },
			{ "key": "H0050001_PCT", "label": "vacant homes", 	"details": "Vacant housing units out of all housing units", "is_percent": True },
			{ "key": "B07001_001E_PCT", "label": "new residents", "details": "Residents who moved into DC in the last year", "is_percent": True },
			{ "key": "B01002_001E",	"label": "median age", "details": "The median age of all residents in the ANC." },
			{ "key": "B19019_001E",	"label": "median household income", "details": "The median income of households in the ANC.", "is_dollars": True },
			{ "key": "POP_DENSITY",	"label": "density (pop/sq-mi)", "details": "Total population divided by the area of the ANC." },
			{ "key": "liquor_licenses",	"label": "liquor licenses",	"details": "Liquor licenses granted by ABRA held by bars and restaurants in the area" },
			{ "key": "building_permits",	"label": "building permits",	"details": "Permits granted by DCRA for construction or alteration in the area" },
						{ "key": "311_requests",    "label": "311 requests",    "details": "Requests to the 311 hotline from this area" },
		]
		for s in census_stats:
			try:
				s["value"] = info["census"][s["key"]]["value"]
			except KeyError:
				s["value"] = 0
			s["grid"] = census_grids[s["key"]]

		# recent ANC documents
		recent_documents = Document.objects.filter(anc=anc).order_by('-created')[0:10]

		# documents that *should* exist
		highlight_documents = []
		for mtg in previous_meetings + ([next_meeting] if next_meeting else []):
			hd_mtg = (mtg, [])
			highlight_documents.append(hd_mtg)

			for doc_type_id, doc_type_name in [(2, "Minutes"), (1, "Agenda")]:
				# in case there are two documents of the same type, just get the first
				def first(qs):
					if qs.count() == 0: raise Document.DoesNotExist()
					return qs[0]

				# find the document
				try:
					doc = first(Document.objects.filter(anc=anc, doc_type=doc_type_id, meeting_date=mtg))
				except Document.DoesNotExist:
					doc = None

				# for meetings that aren't two weeks behind us, if minutes aren't
				# available, don't bother asking for them because they are almost
				# certainly not available yet
				if not doc and doc_type_id == 2 and (now - mtg).days < 14:
					continue

				hd_mtg[1].insert(0, (doc_type_id, doc_type_name, doc) )

				# If minutes exist for a meeting, don't bother displaying an
				# agenda (or ask to upload an agenda) for the meeting.
				if doc and doc_type_id == 2:
					break

		return render(request, self.template_name, {
			'anc': anc,
			'info': info, 
			'documents': recent_documents,
			'highlight_documents': highlight_documents,
			'census_stats': census_stats,
			'next_meeting': next_meeting,
		})


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


class BigMapTemplateView(TemplateView):
	'''This CBV generates the map page. '''
	template_name = 'ancbrigadesite/map.html'
	
	# Add anc_data to the context of our CBV
	def get_context_data(self, **kwargs):
		# Call the base implementation first to get a context
		context = super(BigMapTemplateView, self).get_context_data(**kwargs)
		# Add in anc_data to our CBV
		context['anc_data'] = anc_data_as_json
		return context
	
	 
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
		if request.path != document.get_absolute_url():
			# redirect to canonical URL
			return redirect(document)
		return render(request, self.template_name, {"document": document})
		
# RSS feeds for new documents
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
import dateutil.parser
def make_anc_feed(request, anc):
	
	if anc: anc = anc.upper()

	class ANCRSSFeed(Feed):
		title = settings.APP_NICE_SHORT_NAME if anc is None else ("ANC " + anc + " - " + settings.APP_NICE_SHORT_NAME)
		link = settings.SITE_ROOT_URL + "/" + (anc if anc else "")
		description = "New documents and upcoming meetings for Advisory Neighborhood Commissions on ANCFinder.org."

		def items(self):
			# recent documents
			docs = Document.objects.order_by('-created')
			if anc: docs = docs.filter(anc=anc)
			docs = list(docs[:15])

			# upcoming meetings
			if anc is not None:
				# for an ANC-specific feed, include the next three meetings
				meetings = []
				now = datetime.datetime.now().isoformat()
				for mtgdate, mtginfo in meeting_data[anc]['meetings'].items():
					if mtgdate < now: continue
					meetings.append( (mtgdate, anc, mtginfo) )
				meetings.sort()
				meetings = meetings[:3]
			else:
				# for the site-wide feed, show the next meeting of each ANC
				meetings = []
				now = datetime.datetime.now().isoformat()
				for mtganc, mtgs in meeting_data.items():
					for mtgdate, mtginfo in sorted(mtgs['meetings'].items()):
						if mtgdate < now: continue
						meetings.append( (mtgdate, mtganc, mtginfo) )
						break
				meetings.sort()

			return docs + meetings

		def item_title(self, item):
			if isinstance(item, Document):
				return item.get_display_title()
			else:
				return item[1] + " Meeting on " + dateutil.parser.parse(item[0]).strftime("%B %d")
		def item_description(self, item):
			if isinstance(item, Document):
				return "New Document: " + item.get_display_title() + "."
			else:
				return "A meeting of ANC " + item[1] + " has been scheduled for " + dateutil.parser.parse(item[0]).strftime("%A, %B %d, %Y at %I:%M %p") + "."
		def item_pubdate(self, item):
			if isinstance(item, Document):
				return item.created
			else:
				return dateutil.parser.parse(item[0])
		def item_link(self, item):
			if isinstance(item, Document):
				return settings.SITE_ROOT_URL + item.get_absolute_url()
			else:
				return settings.SITE_ROOT_URL + "/" + item[1] # e.g. /1A
		def item_guid(self, item):
			if isinstance(item, Document):
				return settings.SITE_ROOT_URL + "/document/" + str(item.id)
			else:
				return settings.SITE_ROOT_URL + "/" + item[1] + "/meeting/" + item[0].replace("-", "").replace(":", "") # e.g. /1A/meeting/20140101T000000

	return ANCRSSFeed()(request)
