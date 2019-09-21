#!/bin/bash -e

should_install_apache=true
update_apache_conf=false

project_dir_owner="ubuntu"

virtual_env_location="/home/ubuntu/envs"
virtual_env_name="aaho_venv"

update_supervisor_config=false
update_supervisor_init_script=false

rabbit_mq_password="aahoMQ1.12017"
install_rabbit_mq=false

if [ -e ../../../transiq/static/.htaccess ]
then
        rm ../../../transiq/static/.htaccess
fi
touch ../../../transiq/static/.htaccess
echo "Options +FollowSymlinks" >> ../../../transiq/static/.htaccess
echo "RewriteEngine on" >> ../../../transiq/static/.htaccess
echo "RewriteCond %{REQUEST_URI} !/aaho/js/restapi [NC]" >> ../../../transiq/static/.htaccess
echo "RewriteRule ^(.*)$ https://d2u52eosyz0aln.cloudfront.net/static/\$1 [r=301,nc]" >> ../../../transiq/static/.htaccess
