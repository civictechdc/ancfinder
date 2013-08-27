from django.shortcuts import render
from django.http import Http404, HttpResponse
import datetime

try:
	import json
except ImportError:
	import simplejson as json

anc_data_as_json = open("ancbrigadesite/static/ancs.json").read()
anc_data = json.loads(anc_data_as_json)

def home(request):
	return render(request, 'ancbrigadesite/index.html', { 'anc_data': anc_data_as_json } )

def anc_info(request, anc):
	anc = anc.upper()
	info = anc_data[anc[0]]["ancs"][anc[1]]
	
	info["smd_list"] = sorted(info["smds"].values(), key = lambda s : s["smd"])
	
	prep_hoods(info, True)
	for smd in info["smds"].values():
		prep_hoods(smd, False)
		
	info["census"] = {
		"population": get_census_value_count(info, "tract", "P0010001"),
		"households": get_census_value_count(info, "tract", "P0180002"),
		"family_households": get_census_value_count(info, "tract", "P0180002"),
		"occupied_housing_units": get_census_value_count(info, "tract", "H0040001"),
		"vacant_housing_units": get_census_value_count(info, "tract", "H0050001"),
		"median_age": get_census_value_median(info, "tract", "B01002_001E"),
		"median_income": get_census_value_median(info, "tract", "B19019_001E"),
	}
	
	return render(request, 'ancbrigadesite/anc.html', {'anc': anc, 'info': info})
	
def about(request):
	return render(request, 'ancbrigadesite/about.html')

def share(request):
	return render(request, 'ancbrigadesite/share.html')

def authority(request):
	return render(request, 'ancbrigadesite/authority.html')
	
def elections(request):
	return render(request, 'ancbrigadesite/elections.html')
	
def prep_hoods(info, is_anc):
	def is_part(h):
		if h.get("part-of-neighborhood", 0) < (.9 if is_anc else .6): return "parts of "
		return ""
		
	# First sort by population and remove the smallest neighborhood intersections
	# so long as the cumulative population removed is less than 5% of the total
	# population. These are either degenerate intersections of very small area or
	# non-residential neighborhoods like the Tidal Basin or Union Station.
	hoods = list(info["map"]["neighborhood"])
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
		
	info["neighborhoods"] = hoods
	
def get_census_value_count(anc, gistype, field):
	# sum the values of the intersecting regions multiplied by the percent of that region
	# that intersects with the ANC
	r = 0.0
	for b in anc["map"][gistype]:
		w = b["part-of-tract"]
		v = float(b[field]) # TODO remove float() when this is fixed in the json file
		r += w * v
	return int(round(r))
def get_census_value_median(anc, gistype, field):
	# weight the value by the estimated population in the intersection of the ANC and
	# the region
	r = 0.0
	t = 0.0
	for b in anc["map"][gistype]:
		w = float(b['P0010001'])*b["part-of-tract"] # weight by this value
		v = float(b[field]) # TODO remove float() when this is fixed in the json file
		r += w * v
		t += w
	if t == 0.0: return None
	return int(round(r/t))
	