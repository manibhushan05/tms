#!/bin/bash -e

## update and upgrade packages
echo "[SETUP] Updating system packages..."
sudo apt-get update --fix-missing
sudo apt-get upgrade -y --fix-missing


## install ubuntu dependencies
echo "[SETUP] Installing system dependencies..."
# python dependencies
sudo apt-get install -y python3 python3-dev python3-pip python3-virtualenv ipython3
# postgres
sudo apt-get install -y libpq-dev postgresql postgresql-contrib vim git
# pil/pillow
sudo apt-get install -y libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk
# wkhtmltopdf
sudo apt-get install -y openssl build-essential libssl-dev git git-core libxrender-dev libx11-dev libxext-dev libfontconfig1-dev libfreetype6-dev fontconfig
