Vagrant.configure("2") do |config|
  # The box / OS image
  config.vm.box = "ubuntu/trusty64"
  # Network
  config.vm.network :forwarded_port, guest: 8000, host: 8080
  config.vm.network :private_network, ip: "192.168.33.10"

  # setup
  config.vm.provision "shell", inline: <<-SHELL
     apt-get update
     sudo apt-get install -y sqlite3 libsqlite3-dev python3-pip git
     pip3 install -U pip setuptools wheel
     git clone https://github.com/openwisp/openwisp-network-topology/
     echo "installing openwisp-network-topology"
     cd openwisp-network-topology
     pip install -U .
    SHELL

  # Run a server
  config.vm.provision "shell", inline: <<-SHELL
     cd openwisp-network-topology/tests/
     mv local_settings.example.py local_settings.py
     echo "ALLOWED_HOSTS = [192.168.33.10]" > local_settings.py
     python3 manage.py migrate
    SHELL
end
