#!/bin/bash -e

should_install_apache=false
update_apache_conf=false

project_dir_owner="developer_username"

virtual_env_location="/home/developer_username/env_location"
virtual_env_name="aaho_venv"

update_supervisor_config=true
update_supervisor_init_script=true

rabbit_mq_password="aahoMQ1.12017"
install_rabbit_mq=true