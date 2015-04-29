
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView
from django.conf import settings
from django.utils.timezone import make_aware, get_default_timezone
import datetime, calendar, json, collections, re, copy

import requests
import markdown

from models import Document, anc_data, anc_list, CommissionerInfo


meeting_data = json.loads(open(settings.STATIC_ROOT + "/meetings.json").read())

census_grids = { }

for ward in anc_data.values():
	for anc in ward["ancs"].values():
		for key, info in anc["census"].items():
			census_grids.setdefault(key, []).append( { "anc": anc["anc"], "value": info["value"] } )
for d in census_grids.values():
	d.sort(key = lambda x : x["value"], reverse=True)
	max_val = d[0]["value"]
	for dd in d:
		dd["width"] = int(45 * dd["value"] / max_val)

def get_anc_details(request):
	smd = request.GET['smd']
	anc = smd[0:2]

	num_smds = len(anc_data[anc[0]]['ancs'][anc[1]]['smds'])

	data = {
		"anc": anc,
		"smd": smd[2:4],
		"num_smds": num_smds,
		"bounds": anc_data[smd[0]]['ancs'][smd[1]]['smds'][smd[2:4]]['bounds'],
	}

	data.update( CommissionerInfo.get_all(smd[0:2], smd[2:4]) )

	return HttpResponse(json.dumps(data), content_type="application/json")


def TemplateContextProcessor(request):
	# For master.html's Explore menu, we need the list of ancs
	# by ward.
	import collections
	ancs_by_ward = collections.defaultdict(list)
	for anc in anc_list:
		ancs_by_ward[anc[0]].append(anc)
	ancs_by_ward = [x[1] for x in sorted(ancs_by_ward.items())]

	return {
		"ancs_by_ward": ancs_by_ward,
		"anc_list": anc_list,
	}


class HomeTemplateView(TemplateView):
	template_name = 'ancfindersite/index.html'
			
class AncInfoTemplateView(TemplateView):
	template_name = 'ancfindersite/anc.html'
	# Override the HTTP get method to pass along some additional information
	def get(self, request, anc, *args, **kwargs):
		# Get the ANC and static metadata from ancs.json.
		anc = anc.upper()
		try:
			info = anc_data[anc[0]]["ancs"][anc[1]]
		except KeyError:
			raise Http404()

		# For each SMD, pull in data from our database.
		smds = []
		for smd in info['smds']:
			smddict = copy.deepcopy(info['smds'][smd])
			smddict.update( CommissionerInfo.get_all(anc, smd) )
			smds.append(smddict)
		smds.sort(key = lambda x : x['smd'])

		# Get the committees.
		committees = CommissionerInfo.get(anc, None, 'committees')
		if committees is not None:
			committees = re.sub(r"(^|\n)# ", r"\1### ", committees)
			committees = markdown.markdown(committees)

		# Find the next meeting and the most recent two meetings so we can
		# display related documents for those meetings.
		now = datetime.datetime.now()
		all_meetings = meeting_data.get(anc, {}).get("meetings", {})
		all_meetings = sorted([datetime.datetime.strptime(m, "%Y-%m-%dT%H:%M:%S")
			for m in all_meetings.keys()
			if all_meetings[m].get("status") != "invalid"
			])
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
			{ "key": "P0180002", 	"label": "families", 		"details": "A group of two or more related people residing together", "credit": "US Census" },
			{ "key": "P0180001", 	"label": "households", 		"details": "A house, apartment, or room intended as separate living quarters", "credit": "US Census" },
			{ "key": "P0010001", 	"label": "residents", 		"details": "The total population of the ANC", "credit": "US Census" },
			{ "key": "H0050001_PCT", "label": "vacant homes", 	"details": "Vacant housing units out of all housing units", "credit": "US Census", "is_percent": True },
			{ "key": "B07001_001E_PCT", "label": "new residents", "details": "Residents who moved into DC in the last year", "credit": "US Census", "is_percent": True },
			{ "key": "B01002_001E",	"label": "median age", "details": "The median age of all residents in the ANC", "credit": "US Census" },
			{ "key": "B19019_001E",	"label": "median household income", "details": "The median income of households in the ANC", "credit": "US Census", "is_dollars": True },
			{ "key": "POP_DENSITY",	"label": u"density (pop/mi\u00B2)", "details": "Total population divided by the area of the ANC", "credit": "US Census" },
			{ "key": "liquor_licenses",	"label": "liquor licenses",	"details": "Liquor licenses granted by ABRA held by bars and restaurants in the area", "credit": "ABRA" },
			{ "key": "building_permits",	"label": "building permits",	"details": "Permits granted by DCRA for construction or alteration in the area", "credit": "DCRA" },
						{ "key": "311_requests",    "label": "311 requests",    "details": "Requests to the 311 hotline from this area", "credit": "SeeClickFix" },
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

			has_doc = False
			for doc_type_id, doc_type_name in [(14, "Summary"), (2, "Minutes"), (1, "Agenda")]:
				# If minutes or a summary exist for a meeting, don't bother displaying an
				# agenda (or ask to upload an agenda) for the meeting.
				if has_doc and doc_type_id == 1:
					continue

				# in case there are two documents of the same type, just get the first
				def first(qs):
					if qs.count() == 0: raise Document.DoesNotExist()
					return qs[0]

				# find the document
				try:
					doc = first(Document.objects.filter(anc=anc, doc_type=doc_type_id, meeting_date=mtg))
					has_doc = True
				except Document.DoesNotExist:
					doc = None

				# for meetings that aren't behind us, if a summary isn't available
				# don't bother asking the user to upload one.
				if not doc and doc_type_id == 14 and mtg >= now:
					continue
				
				# for ANCs that have never had a summary posted, don't ask for one either
				if not doc and doc_type_id == 14 and not Document.objects.filter(anc=anc, doc_type=doc_type_id).exists():
					continue

				# for meetings that aren't two weeks behind us, if minutes aren't
				# available, don't bother asking for them because they are almost
				# certainly not available yet
				if not doc and doc_type_id == 2 and (now - mtg).days < 14:
					continue

				hd_mtg[1].insert(0, (doc_type_id, doc_type_name, doc) )

		return render(request, self.template_name, {
			'anc': anc,
			'info': info,
			'smds': smds,
			'committees': committees,
			'documents': recent_documents,
			'highlight_documents': highlight_documents,
			'census_stats': census_stats,
			'next_meeting': next_meeting,
		})


#Using Class Based Views(CBV) to implement our logic
	
class AboutTemplateView(TemplateView):
	'''This CBV generates the about page. '''
	template_name = 'ancfindersite/about.html'


class  ShareTemplateView(TemplateView):
	'''This CBV generates the share page. '''
	template_name = 'ancfindersite/share.html'


class AuthorityTemplateView(TemplateView):
	'''This CBV generates the authority page. '''
	template_name = 'ancfindersite/authority.html'


class BigMapTemplateView(TemplateView):
	'''This CBV generates the map page. '''
	template_name = 'ancfindersite/map.html'	
	 
class LegalTemplateView(TemplateView):
	template_name = 'ancfindersite/legal.html'
	
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
	template_name = 'ancfindersite/document.html'
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
					if mtginfo.get("status") == "invalid": continue
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
						if mtginfo.get("status") == "invalid": continue
						meetings.append( (mtgdate, mtganc, mtginfo) )
						break

			items = docs + meetings
			items.sort(key = lambda item : self.item_pubdate(item), reverse=True)
			return items

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
				return make_aware(dateutil.parser.parse(item[2]["created"]), get_default_timezone())
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

def make_anc_ical(request, anc=None):
	# Collect future meetings and sort after collating meetings across ANCs.
	now = datetime.datetime.now()
	meetings = []
	for mtganc, mtgs in meeting_data.items():
		if anc != None and mtganc.lower() != anc: continue
		for mtgdate, mtginfo in sorted(mtgs['meetings'].items()):
			mtgdate = dateutil.parser.parse(mtgdate)
			if mtgdate < now: continue
			meetings.append( (mtgdate, mtganc, mtginfo) )
	meetings.sort()

	# Make ical.
	from icalendar import Calendar, Event
	cal = Calendar()
	for mtgdate, mtganc, mtginfo in meetings:
		if mtginfo.get("status") == "invalid": continue
		event = Event()
		event.add('dtstart', mtgdate)
		event['summary'] = "ANC %s Meeting" % mtganc
		event['description'] = "See ANCFinder.org for details: http://ancfinder.org/%s" % mtganc
		event['location'] = '; '.join(mtginfo[k] for k in ('building', 'address', 'root') if mtginfo.get(k))
		event['link'] = mtginfo.get("link")
		cal.add_component(event)

	return HttpResponse(cal.to_ical(), "text/calendar" if "mime" not in request.GET else "text/plain")


def mar_lookup_proxy(request):
	''' proxying the DC MAR endpoint because it doesn't seem to work with direct requests from the browser '''

	address = request.GET.get('address')
	if not address:
		raise Http404()

	def mar_request(addr):
		''' put the mar request in a function so we can call it more than once '''
		r = requests.post(
			r'http://citizenatlas.dc.gov/newwebservices/locationverifier.asmx/findLocation2',
			data={'f': 'json', 'str': addr})
		r.raise_for_status()
		return r.json()

	try:
		mar_json = mar_request(address)
	except:
		mar_json = mar_request(address)  # one retry for now

	return HttpResponse(json.dumps(mar_json), content_type="application/json")
