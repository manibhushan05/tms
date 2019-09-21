#!/bin/bash -e

config_dir=$1


if [ ! -f "$config_dir"/requirements.txt ]; then
    echo "[SETUP] ERROR: no local requirements.txt file found, please copy and rename the template.requirements.txt file"
    exit 1
fi

if [ ! -f "$config_dir"/settings.sh ]; then
    echo "[SETUP] ERROR: no local settings.sh file found, please copy and rename the template.settings.sh file"
    exit 1
fi


