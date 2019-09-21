#!/bin/bash -e

tag="SETUP.firewall"

config_dir=$1

echo "[$tag] Setting up Firewall..."

sudo apt-get install libapache2-modsecurity
sudo apachectl -M | grep security
if [ -e /etc/modsecurity/modsecurity.conf-recommended ]
then
	sudo mv /etc/modsecurity/modsecurity.conf-recommended /etc/modsecurity/modsecurity.conf
fi
sudo rm -rf /usr/share/modsecurity-crs
sudo git clone https://github.com/SpiderLabs/owasp-modsecurity-crs.git /usr/share/modsecurity-crs
cd /usr/share/modsecurity-crs 
sudo mv crs-setup.conf.example crs-setup.conf
sudo python3 /usr/share/modsecurity-crs/util/upgrade.py --geoip
sudo cp "$config_dir"/firewall/modsecurity.conf /etc/modsecurity/modsecurity.conf
sudo cp "$config_dir"/firewall/crs-setup.conf /usr/share/modsecurity-crs/crs-setup.conf
sudo cp "$config_dir"/firewall/security2.conf /etc/apache2/mods-enabled/security2.conf

echo "[$tag] Firewall Setup Done"
sudo systemctl restart apache2

