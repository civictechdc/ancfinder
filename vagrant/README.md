To get going with the app, you'll first need Vagrant and VirtualBox.
You can then use the Vagrantfile in this directory to get things
set up.

To provision the vm:
  vagrant up
  vagrant ssh
  /bin/bash provision.sh

Then to start the app:
  cd ancfinder
  source .env/bin/activate
  ./manage.py runserver 0.0.0.0:8000

It'll then be running locally at http://localhost:8000.
