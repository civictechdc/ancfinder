ancfinder
==========

A website about DC's Advisory Neighborhood Commission system.

Contributing
------------

If you plan to contribute to the repo, you should set up your own fork and open pull requests with any commits you make. Please note that all contributions are made under a [CC0 license](LICENSE.md).

If you're not familiar with forking, Github has a [useful guide](https://help.github.com/articles/fork-a-repo).

Installation using Vagrant
--------------------------

First get [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/). Once they're both installed, clone the ANC Finder repo on your machine:

	git clone --recursive https://github.com/codefordc/ancfinder
	cd ./ancfinder
	git submodule init
	git submodule update

Then get the Vagrant box setup (you're still in the 'ancfinder' directory):

	vagrant up

Log into the newly-established VM:

	vagrant ssh

and then run the script that will take care of all the dependencies:

	/bin/bash provision.sh

The new Vagrant-managed VM with the application and its dependencies is now all ready to go. (If instead you do not want to use Vagrant, you can run all the steps listed in 'provision.sh' on your machine directly.)

Running the Site
----------------

Once you have finished the steps above, you're ready to start the app from within the Vagrant box (you have already ssh'd into the box):

	cd ancfinder
	source .env/bin/activate
	./manage.py runserver 0.0.0.0:8000

Then point your browser to http://localhost:8000 and if you see the ANC Finder site, you're all set.


Updating the Code
-----------------

As we make code changes you may need to run:

	git pull --rebase
	git submodule update --init
	./manage.py syncdb

If we modify the database schema, you may need to delete ancfindersite/database.sqlite and run `./manage.py syncdb` to recreate your database from scratch since we don't currently have a way to upgrade database schemas.

Updating Static Data
--------------------

The ANC/SMD metadata is stored statically in `static/ancs.json`. To update this file
from our Google Doc, our scrapers, and other external data sources, run:

	python3 scripts/update_anc_database.py

You will need to provide your Google email & password and a Census API key, which you can get at http://www.census.gov/developers/tos/key_request.html. For convenience, you can also store these credentials in a file named "update_anc_database_creds.py" in this (root) directory and put in it:

	google_email="your.address@gmail.com"
	google_password="your google password"
	census_api_key="your Census API key"

You can also selectively update just some of the data (because updating some takes a long time) using command line arguments:

	python3 scripts/update_anc_database.py [--base] [--terms] [--gis] [--neighborhoods] [--census] [--census-analysis]

And to fetch the latest ANC meetings calendar (note that it currently requires Python 2):

	python scripts/update_meeting_database.py

There are also several scripts to grab data for use in `update_anc_database.py`. They are:

        scripts/update_abra.py # Liquor licenses
        scripts/update_building_permits.py # Building permits
        scripts/update_terms.py # Terms served by commissioners
		scripts/update_311.py # 311 requests
		scripts/update_crimes.py # Doesn't really do anything right now

All of the scripts should be run occasionally to make sure the data shown on the site is up-to-date.

Deployment
----------

When deploying the code to the live server, remember to update the static files:

	./manage.py collectstatic
