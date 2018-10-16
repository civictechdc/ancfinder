Ancfinder
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

Running the Site with Docker
----------------

### With Docker

1. Go to the root of the cloned directory and run `docker-compose up -d`. This will start all the required pieces of infrastructure as well as the application.
3. To stop the application `docker-compose stop`; it can be restarted with `docker-compose start`.

To open the site in a browser, direct your browser to http://localhost:80.

### Without Docker

1. Go to the root of the cloned directory and run `python3 mange.py runserver`
2. Use ctrl + C at the command line to stop the process.

To open the site in a browser, direct your browser to http://localhost:80

Updating the Code and Database
-----------------

As we make code changes you may need to run:

	git pull --rebase
	./manage.py migrate
