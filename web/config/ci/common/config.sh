#!/bin/bash -e

script_version_code="1.0.1"

if [ $# -eq 0 ]; then
    echo "No deploy environment provided"
    exit 1
fi

if [ $1 = "dev" ] || [ $1 = "prod" ] || [ $1 = "local" ] || [ $1 = "stage" ]; then
    deploy_env="$1"
else
    echo "[SETUP] ERROR: unknown deploy environment - '$1', allowed are 'dev', 'prod', 'stage'  and 'local'"
    exit 1
fi

script_version="$script_version_code-$deploy_env"
django_settings="transiq.settings.$deploy_env"

script_dir="$( dirname "$(readlink -f "$0")" )"

python_dir_rel="$script_dir"/../../../transiq
config_dir_rel="$script_dir"/../"$deploy_env"

python_dir="$(readlink -f "$python_dir_rel")"
config_dir="$(readlink -f "$config_dir_rel")"

config_env_settings_script="$config_dir"/settings.sh
config_aws_settings_script="$config_dir"/awsupdate.sh

config_apache_script="$script_dir"/config_apache.sh
config_celery_script="$script_dir"/config_celery.sh
config_supervisor_script="$script_dir"/config_supervisor.sh
config_system_script="$script_dir"/config_system.sh
config_env_setup_script="$script_dir"/config_env.sh
config_metabase_script="$script_dir"/config_metabase.sh
config_firewall_script="$script_dir"/config_firewall.sh

generate_local_celery_config_script="$script_dir"/generate_local_celery_config.sh
validate_local_config_script="$config_dir"/validate_local_config.sh


echo "[SETUP] Aaho Setup Script Version $script_version"

if [ "$deploy_env" = "local" ]; then
    . "$validate_local_config_script" "$config_dir"
fi

# defaults
should_install_apache=true
should_install_supervisor=true

project_dir_owner="ubuntu"

virtual_env_location="/home/ubuntu/envs"
virtual_env_name="aaho_venv"

rabbit_mq_password="aahoMQ1.12017"

# overrides
source "$config_env_settings_script"


virtual_env_path="$virtual_env_location"/"$virtual_env_name"


if [ "$deploy_env" = "local" ]; then
    . "$generate_local_celery_config_script" "$config_dir" "$python_dir" "$virtual_env_path"
fi


#if [ "$deploy_env" = "dev" ]; then
#    . "$config_metabase_script"
#fi

# run system config
. "$config_system_script"


# run apache config
if [ "$should_install_apache" = true ]; then
    . "$config_apache_script" "$config_dir"
fi


# run rabbit mq, celery config
. "$config_celery_script" "$rabbit_mq_password"


# if production, run tests on a test virtual environment first
#if [ "$deploy_env" = "prod" ] || [ "$deploy_env" = "stage" ]; then
#    # run pip-env-python config on a test env
#    test_env_name="$virtual_env_name"_test
#    . "$config_env_setup_script" "$config_dir" "$virtual_env_location" "$test_env_name" "$project_dir_owner"
#
#    # run tests on the test env
#    cd "$python_dir" && "$virtual_env_location"/"$test_env_name"/bin/python3 manage.py test --settings="$django_settings" --noinput -v 2
#    cd -
#fi


# run pip-env-python config
. "$config_env_setup_script" "$config_dir" "$virtual_env_location" "$virtual_env_name" "$project_dir_owner"


# configure supervisor
if [ "$should_install_supervisor" = true ]; then
    . "$config_supervisor_script" "$config_dir" "$script_dir"
fi

# run tests
if [ "$deploy_env" = "dev" ]; then
    cd "$python_dir" && "$virtual_env_path"/bin/python3 manage.py test --parallel=4 --keepdb --noinput -v 2
fi

# IMPORTANT! creating migration files and running migrations is the developer's job, since it might frequently require human intervention

# if production, migrate db
if [ "$deploy_env" = "prod" ] || [ "$deploy_env" = "stage" ]; then
    # Migration
    cd "$python_dir" && "$virtual_env_path"/bin/python3 manage.py migrate --settings="$django_settings" --noinput

    # AWS Sync up
    if [ -e "$config_aws_settings_script" ]
    then
        chmod u+x "$config_aws_settings_script"
        . "$config_aws_settings_script"
    fi
fi

# Firewall Setup for all envs

#if [ -e "$config_firewall_script" ]
#then
#	chmod u+x "$config_firewall_script"
#	. "$config_firewall_script" "$script_dir"
#fi

# wkhtmltopdf Lib

sudo aws s3 cp s3://aahodocumentstest/wkhtmltox-0.12.5-dev-2b3f8bb_linux-generic-amd64.tar.xz "$script_dir"/../../../../.  --region ap-south-1
sudo tar -xf "$script_dir"/../../../../wkhtmltox-0.12.5-dev-2b3f8bb_linux-generic-amd64.tar.xz -C "$script_dir"/../../../../.
if [ -e /usr/bin/wkhtmltopdf ]
then
	sudo rm -rf /usr/bin/wkhtmltopdf
fi
sudo ln -s "$script_dir"/../../../../wkhtmltox/bin/wkhtmltopdf /usr/bin/wkhtmltopdf
sudo mv "$script_dir"/../../../../wkhtmltox-0.12.5-dev-2b3f8bb_linux-generic-amd64.tar.xz /tmp/

# ask apache to restart
sudo a2enmod rewrite
sudo service apache2 restart



