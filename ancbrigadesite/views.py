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
		return h["part-of-neighborhood"] < .9
	
	# Filter out neighborhoods that are less than 1% in the ANC/SMD.
	info["map"]["neighborhood"] = [h for h in info["map"]["neighborhood"] if h["part-of-neighborhood"] > .01]

	# Sort neighborhoods by putting the ones that are "entirely" contained in this
	# ANC/SMD first, and then sort from most coverage of the object to least coverage.
	info["map"]["neighborhood"].sort(key = lambda h : (is_part(h), -h["part-of-" + ("anc" if is_anc else "smd")]))
	
	# For a nice string for display.
	hoods = [("part of " if is_part(h) else "") + h["name"] for h in info["map"]["neighborhood"]]
	if len(hoods) <= 2:
		hoods = " and ".join(hoods)
	else:
		hoods[-1] = "and " + hoods[-1]
		hoods = ", ".join(hoods)
		
	info["neighborhoods"] = hoods
	