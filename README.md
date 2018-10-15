ancfinder
==========

A website about DC's Advisory Neighborhood Commission system.

Contributing
------------

If you plan to contribute to the repo, you should set up your own fork and open pull requests with any commits you make. Please note that all contributions are made under a [CC0 license](LICENSE.md).

If you're not familiar with forking, Github has a [useful guide](https://help.github.com/articles/fork-a-repo).

Getting Started
---------------

In order to get the site running locally you'll want to start by creating an account for Docker, download, and install the program. The community edition can be downloaded [here](https://www.docker.com/community-edition).

Once forked, clone the forked repository to your computer.

	git clone --recursive https://github.com/codefordc/ancfinder
	cd ./ancfinder
	git submodule init
	git submodule update

Running the Site
----------------

1. Copy `sample.env` into a file called `.env`.  This file is GIT ignored, so please change any credentials to fit your local work.
2. Go to the root of the cloned directory and run `docker-compose up`. This will start all the required pieces of infrastructure as well as the application.
3. To stop the application `ctrl-c`; it can be restarted with `docker-compose start`.

Alternatively, `docker-compose up -d` will spawn it into a background thread.

To open the site in a browser, direct your browser to http://localhost:80; this might take a few minutes.

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
from our external data sources, run:

	python3 scripts/update_anc_database.py

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
