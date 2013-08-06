from django.shortcuts import render
from django.http import Http404, HttpResponse
import datetime

def home(request):
	return render(request, 'index.html')

def anc_info(request, anc):
	anc = anc.upper()
	return render(request, 'anc.html', {'anc': anc})
	
def about(request):
	return render(request, 'about.html')

def share(request):
	return render(request, 'share.html')

def authority(request):
	return render(request, 'authority.html')
	
def elections(request):
	return render(request, 'elections.html')