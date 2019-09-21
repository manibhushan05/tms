#!/bin/bash -e

config_dir=$1
project_location=$2
env_location=$3

echo "

; celery, celerybeat, rabbitmq

[program:aahobeat]
command=$env_location/bin/celery -A transiq beat -s /var/run/celery/celerybeat-schedule -l info --pidfile=/tmp/aahobeat.pid
directory=$project_location/
stdout_logfile=/var/log/celery/aahobeat-out.log
stderr_logfile=/var/log/celery/aahobeat-err.log
autostart=true
autorestart=true
user=celery
startsecs=10
stopwaitsecs=300

[program:aahoworker]
numprocs=4
process_name=worker%(process_num)s
command=$env_location/bin/celery -A transiq worker -l info -n worker%(process_num)s.%%h --pidfile=/tmp/aaho-worker%(process_num)s.pid
directory=$project_location/
stdout_logfile=/var/log/celery/aahoworker-out.logS
stderr_logfile=/var/log/celery/aahoworker-err.log
autostart=true
autorestart=true
user=celery
startsecs=10
stopwaitsecs=300

" > "$config_dir"/supervisor/extra/celery.conf