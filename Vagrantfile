# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ancfinder"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # it seems like we need more than 512M to compile certain deps
  config.vm.provider "virtualbox" do |vb|
     vb.customize ["modifyvm", :id, "--memory", "1024"]
  end

  config.vm.provision "shell" do |s|
    s.inline = "sudo -u vagrant /bin/bash /vagrant/provision.sh"
  end

end
