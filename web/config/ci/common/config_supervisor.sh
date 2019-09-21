#!/bin/bash -e

tag="SETUP.supervisor"

# variables
config_dir=$1
script_dir=$2

supervisor_extra_dir="$config_dir"/supervisor/extra
supervisor_config_file="$script_dir"/supervisor/supervisord.conf
supervisor_init_script="$script_dir"/supervisor/service/supervisord.sh

live_supervisor_dir=/etc/supervisord
live_supervisor_extra_dir="$live_supervisor_dir"/extra
live_supervisor_config_file="$live_supervisor_dir"/supervisord.conf
live_supervisor_init_dir=/etc/init.d
live_supervisor_init_script="$live_supervisor_init_dir"/supervisord


if command -v supervisord &>/dev/null; then
    echo "[$tag] Supervisor Already installed"
else
    echo "[$tag] Installing Supervisor"
    #sudo pip3 install -U supervisor
    sudo pip3 install git+https://github.com/Supervisor/supervisor@master
fi

copy_init_script=false
delete_old_init=false

if sudo test -f "$live_supervisor_init_script"; then
    echo "[$tag] Supervisor init script found"
    if sudo cmp -s "$live_supervisor_init_script" "$supervisor_init_script"; then
        echo "[$tag] Init script unchanged"
    else
        echo "[$tag] Init script changed"
        delete_old_init=true
    fi
else
    echo "[$tag] Supervisor init script not found"
    copy_init_script=true
fi


delete_old_config=false
copy_new_config=false

if sudo test -f "$live_supervisor_config_file"; then
    echo "[$tag] Supervisor config file found"
    if sudo cmp -s "$live_supervisor_config_file" "$supervisor_config_file"; then
        echo "[$tag] Config file unchanged"
    else
        echo "[$tag] Config file changed"
        delete_old_config=true
    fi
else
    echo "[$tag] Supervisor config file not found"
    copy_new_config=true
fi

# check for new and updated config files
for file in "$supervisor_extra_dir"/*.conf; do
    conf_name="$(basename "$file")"
    if sudo test -f "$live_supervisor_extra_dir"/"$conf_name"; then
        if sudo cmp -s "$live_supervisor_extra_dir"/"$conf_name" "$supervisor_extra_dir"/"$conf_name"; then
            echo "[$tag]     - $conf_name unchanged"
        else
            echo "[$tag]     - $conf_name changed"
            delete_old_config=true
        fi
    else
        echo "[$tag]     - $conf_name not found"
        copy_new_config=true
    fi
done

# check for config files that were deleted
if sudo test -d "$live_supervisor_extra_dir"; then
    for file in "$live_supervisor_extra_dir"/*.conf; do
        conf_name="$(basename "$file")"
        if sudo test -f "$supervisor_extra_dir"/"$conf_name"; then
            :
        else
            echo "[$tag]     - $conf_name deleted"
            delete_old_config=true
        fi
    done
fi

if [ "$delete_old_config" = true ]; then
    echo "[$tag] Deleting old supervisor conf files..."
    sudo rm -f "$live_supervisor_config_file"
    sudo rm -f "$live_supervisor_extra_dir"/*.conf
    sudo rmdir "$live_supervisor_extra_dir"
    sudo rmdir "$live_supervisor_dir"
    copy_new_config=true
fi

supervisor_config_updated=false

if [ "$copy_new_config" = true ]; then
    echo "[$tag] Copy new supervisor conf files..."
    sudo mkdir -p "$live_supervisor_dir" "$live_supervisor_extra_dir" /var/log/supervisord
    sudo cp "$supervisor_config_file" "$live_supervisor_dir"
    sudo cp "$supervisor_extra_dir"/*.conf "$live_supervisor_extra_dir"

    echo "[$tag] Set permissions for new supervisor conf files..."
    sudo chmod 644 "$live_supervisor_config_file"
    sudo chmod 644 "$live_supervisor_extra_dir"/*.conf
    supervisor_config_updated=true
fi

if [ "$delete_old_init" = true ]; then
    echo "[$tag] Deleting old supervisor init script..."
    sudo rm -f "$live_supervisor_init_script"
    copy_init_script=true
fi

init_script_updated=false

if [ "$copy_init_script" = true ]; then
    echo "[$tag] Copy new supervisor init script..."
    sudo cp "$supervisor_init_script" "$live_supervisor_init_dir"
    sudo mv "$live_supervisor_init_dir"/supervisord.sh "$live_supervisor_init_script"
    sudo chmod 755 "$live_supervisor_init_script"
    sudo update-rc.d supervisord defaults
    init_script_updated=true
fi

if sudo test -S /tmp/supervisor.sock; then
    echo "[$tag] Socket file found, assuming supervisor has run before on the system..."
else
    echo "[$tag] Socket file not found, assuming first time run..."
    sudo supervisord -c "$live_supervisor_config_file"
fi

if [ "$init_script_updated" = true ]; then
    echo "[$tag] Testing new init script..."
    sudo service supervisord stop || echo "[$tag]    - supervisor already not running"
    sudo service supervisord start
fi

if [ "$supervisor_config_updated" = true ]; then
    echo "[$tag] Updating new supervisor config..."
    sudo supervisorctl -c "$live_supervisor_config_file" reread
    sudo supervisorctl -c "$live_supervisor_config_file" update
fi

echo "[$tag] Restarting supervisor tasks..."
sudo supervisorctl -c "$live_supervisor_config_file" restart all

echo "[$tag] Supervisor config done..."
sudo supervisorctl -c "$live_supervisor_config_file" status

