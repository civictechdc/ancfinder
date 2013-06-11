ancbrigade
==========

A website about DC's Advisory Neighborhood Commission system.

The ANC/SMD metadata is stored statically in www/ancs.json. To update this file
from our Google Doc and ScraperWiki scraper, run:

	python get_googledoc.py > www/ancs.json
	
When testing this site from your own computer, if you're using Chrome you'll
need to bypass a security setting so that index.html can access ancs.json
from your local drive. Close all Chrome windows and then start Chrome with:

	google-chrome --allow-file-access-from-files www/index.html 

