ancbrigade
==========

A website about DC's Advisory Neighborhood Commission system.

The ANC/SMD metadata is stored statically in www/ancs.json. To update this file
from our Google Doc and ScraperWiki scraper, run:

	python get_googledoc.py > www/ancs.jsonp

And to fetch the latest ANC meetings calendar:
	
	python update_meeting_database.py
	

