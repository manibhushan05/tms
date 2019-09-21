#!/bin/bash -e

tag="SETUP.env"

config_dir=$1
env_location=$2
env_name=$3
user=$4

existing_env="$env_location"/"$env_name"
pip_requirements_file="$config_dir"/requirements.txt


## update pip and install python dependencies
echo "[$tag] Updating pip..."
sudo pip3 install -U pip
sudo pip3 install virtualenv

# if there is no virtual env directory, assume that this is the first time setup is being done on this system
if [ ! -d "$existing_env" ]; then
    echo "[$tag] Virtual env does not exist, creating..."
    sudo mkdir -p "$env_location"
    sudo chown "$user":"$user" "$env_location"
    cd "$env_location"
    sudo virtualenv "$env_name"
    cd -
else
    echo "[$tag] Virtual env already exists, skipping creation..."
fi

# install/update python pip libraries
echo "[$tag] Updating pip requirements..."
"$existing_env"/bin/pip3 install -U -r "$pip_requirements_file"
