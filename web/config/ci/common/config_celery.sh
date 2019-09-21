#!/bin/bash -e

tag="SETUP.celery"

password=$1

install_rabbit_mq=false


# install rabbitmq is rabbitmqctl throws error
sudo rabbitmqctl status || (echo "[$tag] Rabbit MQ not installed, Installing..." && sudo apt-get install -y rabbitmq-server)

user_exists=`sudo rabbitmqctl list_users | grep aaho | wc -l`
if [ "$user_exists" -ne 0 ]; then
    echo "[$tag] User already exists..."
    create_user=false
else
    create_user=true
fi

if [ "$create_user" = true ]; then
    echo "[$tag] Creating Rabbit MQ user..."
    sudo rabbitmqctl change_password guest "$password"
    sudo rabbitmqctl add_user aaho "$password" || echo "    - rabbitmqctl add_user aaho failed, probably already exists"
    sudo rabbitmqctl add_vhost aaho || echo "    - rabbitmqctl add_vhost aaho failed, probably already exists"
    sudo rabbitmqctl set_permissions -p aaho aaho ".*" ".*" ".*"
fi

# setup celery user and dirs
if id celery >/dev/null 2>&1; then
    echo "[$tag] The user 'celery' already exists, skip creating celery user, group, and log folders"
else
    echo "[$tag] User 'celery does not exist, creating..."
    sudo addgroup celery || echo "    - addgroup celery failed, probably already exists"
    sudo adduser --system --no-create-home --shell /bin/sh --ingroup celery celery || echo "    - adduser celery failed, probably already exists"
    sudo mkdir -p /var/log/celery
    sudo chown celery:celery /var/log/celery
    sudo mkdir -p /var/run/celery
    sudo chown celery:celery /var/run/celery
fi


celery_beat_schedule_file="/var/run/celery/celerybeat-schedule"

# setup celery-beat
if sudo test -f "$celery_beat_schedule_file"; then
    echo "[$tag] celerybeat-schedule found"
else
    echo "[$tag] celerybeat-schedule not found, creating"
    sudo mkdir -p /var/run/celery
    sudo chown celery:celery /var/run/celery
    sudo touch "$celery_beat_schedule_file"
    sudo chown celery:celery "$celery_beat_schedule_file"
fi