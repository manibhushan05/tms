#!/bin/bash -e

sudo pip install awscli
sudo aws s3 sync "$script_dir"/../../../transiq/static/ s3://aahodocumentstest/static/ --region ap-south-1 --delete
sudo aws cloudfront create-invalidation --distribution-id E2081SVNQL9LU1 --path /static/aaho/*

sudo apt --yes install jq
sudo aws ec2 create-image --instance-id $(cat /var/lib/cloud/data/instance-id) --name ProdAMI_$(date +%d%m%Y-%M.%S) --description "An AMI for my prod server" --no-reboot --region ap-south-1 > ami.json

aws autoscaling create-launch-configuration --launch-configuration-name ProdLC_$(cat ami.json | jq '.ImageId' | sed 's/"//g') --key-name aahoproduction --image-id $(cat ami.json | jq '.ImageId' | sed 's/"//g') --instance-type t2.medium --security-groups sg-8234aee9 --iam-instance-profile S3-Admin-Access --instance-monitoring Enabled=false --block-device-mappings "[{\"DeviceName\":\"/dev/sda1\",\"Ebs\":{\"VolumeSize\":100}}]" --region ap-south-1

aws autoscaling update-auto-scaling-group --auto-scaling-group-name ProdASG --launch-configuration-name ProdLC_$(cat ami.json | jq '.ImageId' | sed 's/"//g') --region ap-south-1
