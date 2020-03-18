#e -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
VAGRANTFILE_LOCAL = 'Vagrantfile.local'

MM_USERID=ENV['MAXMIND_USERID']
MM_LIC=ENV['MAXMIND_LIC']
CSIRTG_TOKEN=ENV['CSIRTG_TOKEN']

$script = <<SCRIPT
echo "export MAXMIND_USERID=#{MM_USERID}" | sudo -u vagrant -H tee -a /home/vagrant/.profile
echo "export MAXMIND_LIC=#{MM_LIC}" | sudo -u vagrant -H tee -a /home/vagrant/.profile
echo "export CSIRTG_TOKEN=#{CSIRTG_TOKEN}" | sudo -u vagrant -H tee -a /home/vagrant/.profile

apt-get update -y
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose python3-dev aptitude libsnappy-dev python3-pip

usermod -aG docker vagrant

echo "UserId #{MM_USERID}" > /etc/GeoIP.conf
echo "LicenseKey #{MM_LIC}" >> /etc/GeoIP.conf 
echo 'ProductIds GeoLite2-Country GeoLite2-City GeoLite2-ASN' | sudo tee -a /etc/GeoIP.conf

sudo -H -u vagrant pip3 install geoip2 'cifsdk>=5.0b4,<6.0'
sudo -H -u vagrant sh -c 'cp /vagrant/docker-compose.yml /home/vagrant/'
sudo -H -u vagrant mkdir /home/vagrant/data
#sudo -E -H -u vagrant sh -c 'cd /home/vagrant && docker-compose pull'

SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", inline: $script

  config.vm.box = 'ubuntu/bionic64'

  config.vm.network :forwarded_port, guest: 5000, host: 5000

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--cpus", "2", "--ioapic", "on", "--memory", "2048" ]
  end

  if File.file?(VAGRANTFILE_LOCAL)
    external = File.read VAGRANTFILE_LOCAL
    eval external
  end
end
