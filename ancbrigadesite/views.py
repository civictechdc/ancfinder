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
	return render(request, 'ancbrigadesite/anc.html', {'anc': anc, 'info': info})
	
def about(request):
	return render(request, 'ancbrigadesite/about.html')

def share(request):
	return render(request, 'ancbrigadesite/share.html')

def authority(request):
	return render(request, 'ancbrigadesite/authority.html')
	
def elections(request):
	return render(request, 'ancbrigadesite/elections.html')