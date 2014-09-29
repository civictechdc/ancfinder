cd ~vagrant
sudo apt-get -y install git
curl https://bootstrap.pypa.io/get-pip.py > ~/get-pip.py
sudo python ~/get-pip.py
rm ~/get-pip.py
sudo pip install virtualenv
git clone --recursive https://github.com/codefordc/ancfinder
cd ./ancfinder
git submodule init
git submodule update
sudo apt-get -y install libpq-dev libxml2 libxslt1.1 libxml2-dev libxslt1-dev python-libxml2
sudo apt-get -y install python-libxslt1 python-dev libyaml-dev
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
wget -O static/ancs.json http://ancfinder.org/static/ancs.json
wget -O static/meetings.json http://ancfinder.org/static/meetings.json
rm ~/provision.sh

