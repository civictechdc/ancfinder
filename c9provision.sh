curl https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py
sudo python /tmp/get-pip.py
rm /tmp/get-pip.py
sudo pip install virtualenv

sudo apt-get -y install git
sudo apt-get -y install libpq-dev libxml2 libxslt1.1 libxml2-dev libxslt1-dev python-libxml2
sudo apt-get -y install python-libxslt1 python-dev libyaml-dev

git submodule init
git submodule update

sudo pip install -r requirements.txt
wget -O static/ancs.json http://ancfinder.org/static/ancs.json
wget -O static/meetings.json http://ancfinder.org/static/meetings.json
python manage.py syncdb --noinput