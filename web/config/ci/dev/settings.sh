#!/bin/bash -e

should_install_apache=true
update_apache_conf=true

project_dir_owner="jenkins"

virtual_env_location="/home/ubuntu/envs"
virtual_env_name="aaho_venv"

update_supervisor_config=true
update_supervisor_init_script=false

rabbit_mq_password="aahoMQ1.12017"
install_rabbit_mq=false
