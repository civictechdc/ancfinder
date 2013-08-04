from django.shortcuts import render
from django.http import Http404, HttpResponse
import datetime
import simplejson as json

"""def load_json(smd):
	json_data = open("{{ STATIC_URL }}ancs.jsonp")
	anc_data = json.load(json_data)
	ward = anc_data[str(smd[0])]
	anc = anc_data["anc"]
	smd = anc_data
	smd_commissioner = anc_data
	json_data.close()"""

def home(request):
	return render(request, 'index.html')

def smd_info(request, smd):
	smd = smd.upper()
	return render(request, 'smd.html', {'smd': smd})
	
def about(request):
	return render(request, 'about.html')

def share(request):
	return render(request, 'share.html')

def authority(request):
	return render(request, 'authority.html')
	
def elections(request):
	return render(request, 'elections.html')