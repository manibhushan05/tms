#!/bin/bash -e

tag="SETUP.Apache"


config_dir=$1

ssl_key_file="aaho.in.key"
conf_filename="aaho.conf"

new_apache_config_file="$config_dir"/apache/"$conf_filename"
new_ssl_key_file="$config_dir"/ssl/private/"$ssl_key_file"

live_apache_config_dir=/etc/apache2/sites-available
live_apache_config_file="$live_apache_config_dir"/"$conf_filename"

live_ssl_cert_dir=/etc/apache2/ssl
live_ssl_key_dir=/etc/ssl/private
live_ssl_key_file="$live_ssl_key_dir"/"$ssl_key_file"


# SSL config
remove_old_ssl_config=false
copy_ssl_files=false

if sudo test -f "$live_ssl_key_file"; then
    echo "[$tag] Live SSL key found"
    if sudo cmp -s "$new_ssl_key_file" "$live_ssl_key_file"; then
        echo "[$tag] SSL key unchanged"
    else
        echo "[$tag] SSL key updated"
        remove_old_ssl_config=true
    fi
else
    echo "[$tag] Live SSL key not found"
    copy_ssl_files=true
fi

if [ "$remove_old_ssl_config" = true ]; then
    echo "[$tag] Removing old SSL files..."
    sudo rm -f "$live_ssl_cert_dir"/*.crt
    sudo rm -f "$live_ssl_cert_dir"/*.csr
    sudo rmdir "$live_ssl_cert_dir"
    sudo rm -f "$live_ssl_key_file"
    copy_ssl_files=true
fi

if [ "$copy_ssl_files" = true ]; then
    echo "[$tag] Copying new SSL files..."
    sudo mkdir -p "$live_ssl_cert_dir"
    sudo cp "$config_dir"/ssl/*.crt "$live_ssl_cert_dir"
    sudo cp "$config_dir"/ssl/*.csr "$live_ssl_cert_dir"
    sudo cp "$new_ssl_key_file" "$live_ssl_key_dir"
    sudo chmod 600 "$live_ssl_cert_dir"/*.* || echo ""
    sudo chmod 700 "$live_ssl_cert_dir" || echo ""
    sudo chmod 640 "$live_ssl_key_file" || echo ""
fi


# apache config
install_apache=false
update_apache_conf=false

if sudo test -f "$live_apache_config_file"; then
    echo "[$tag] Live apache conf file found"
    if sudo cmp -s "$new_apache_config_file" "$live_apache_config_file"; then
        echo "[$tag] Apache conf unchanged"
    else
        echo "[$tag] Apache conf updated"
        update_apache_conf=true
    fi
else
    echo "[$tag] Live apache conf file not found"
    install_apache=true
fi


if [ "$install_apache" = true ]; then
    echo "[$tag] Installing apache..."
    # install apache and mod-wsgi
    sudo apt-get install -y apache2 apache2-dev libapache2-mod-wsgi-py3

    sudo a2enmod wsgi
    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo a2enmod headers
    sudo a2enmod ssl
    sudo a2dissite 000-default
    sudo a2dissite default-ssl
    sudo a2dissite ci || echo ""
    update_apache_conf=true
fi


if [ "$update_apache_conf" = true ]; then
    # update the config file
    echo "[$tag] Updating apache config..."
    sudo cp "$new_apache_config_file" "$live_apache_config_dir"
    sudo a2ensite "$conf_filename"

    sudo service apache2 restart
fi
