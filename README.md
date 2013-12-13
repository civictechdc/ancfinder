ancbrigade
==========

A website about DC's Advisory Neighborhood Commission system.

Contributing
------------

If you plan to contribute to the repo, you should set up your own fork and open pull requests with any commits you make. 

If you're not familiar with forking, Github has a [useful guide](https://help.github.com/articles/fork-a-repo).

Dependencies
------------

Set up your environment, install dependencies, and set up the site database:

	git clone --recursive https://github.com/codefordc/ancbrigade
        cd ./ancbrigade
	virtualenv .env # maybe one day we'll use '-p python3' but dotcloud makes that harder
	. .env/bin/activate
	sudo apt-get install libxslt1-dev
	pip install -r requirements.txt
	./manage.py syncdb
	
Note --recursive on 'git clone' to get the submodule dependencies.

If it seems like you're missing stuff, also try 'git submodule init; git submodule update".

Running the Site
----------------

Just run:

	. .env/bin/activate
	./manage.py runserver
	
Then view the site in your browser at the address shown to you.

Updating the Code
-----------------

As we make code changes you may need to run:

	git pull --rebase
	git submodule --init update
	./manage.py syncdb

If we modify the database schema, you may need to delete ancbrigadesite/database.sqlite and run `./manage.py syncdb` to recreate your database from scratch since we don't currently have a way to upgrade database schemas.

Updating Static Data
--------------------

The ANC/SMD metadata is stored statically in ancbrigadesite/static/ancs.json. To update this file
from our Google Doc, our ScraperWiki scraper, and other external data sources, run:

	python3 update_anc_database.py

You will need to provide your Google email & password and a Census API key, which you can get at http://www.census.gov/developers/tos/key_request.html. For convenience, you can also store these credentials in a file named "update_anc_database_creds.py" in this directory and put in it:

	google_email="your.address@gmail.com"
	google_password="your google password"
	census_api_key="your Census API key"

You can also selectively update just some of the data (because updating some takes a long time) using command line arguments:
	
	python3 update_anc_database.py [--base] [--terms] [--gis] [--neighborhoods] [--census] [--census-analysis]

And to fetch the latest ANC meetings calendar:
	
	python3 update_meeting_database.py

There are also several scripts to grab data for use in `update_anc_database.py`. They are:

        update_abra.py # Liquor licenses
        update_building_permits.py # Building permits
        update_crimes.py # Crimes reported
        update_terms.py # Terms served by commissioners

All of the scripts should be run occasionally to make sure the data shown on the site is up-to-date.

Deployment
----------

We're currently deploying to dotCloud.

	sudo pip install dotcloud
	dotcloud setup
	dotcloud connect ancbrigade
	dotcloud push # push changes to the live site
	
