from django.shortcuts import render
from django.http import Http404, HttpResponse
import datetime

try:
	import json
except ImportError:
	import simplejson as json

anc_data = json.load(open("ancpage/static/ancs.json"))

def home(request):
	return render(request, 'ancpage/index.html')

def anc_info(request, anc):
	anc = anc.upper()
	info = anc_data[anc[0]]["ancs"][anc[1]]
	return render(request, 'ancpage/anc.html', {'anc': anc, 'info': info})
	
def about(request):
	return render(request, 'ancpage/about.html')

def share(request):
	return render(request, 'ancpage/share.html')

def authority(request):
	return render(request, 'ancpage/authority.html')
	
def elections(request):
	return render(request, 'ancpage/elections.html')