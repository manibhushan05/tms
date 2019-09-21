#!/bin/bash -e

sudo apt-get install -y openjdk-9-jre-headless

sudo mkdir -p /var/log/metabase
sudo chown ubuntu:ubuntu /var/log/metabase