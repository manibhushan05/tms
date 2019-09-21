#!/bin/bash -e

if [ ! -d /home/ubuntu/aaho ]; then
	mkdir /home/ubuntu/aaho
fi
if [ ! -d /home/ubuntu/aaho/web ]; then
	mkdir /home/ubuntu/aaho/web
else
	rm -rf /home/ubuntu/aaho/web/*
fi
#if [ "$DEPLOYMENT_GROUP_NAME" == "stage" ]
#then
#	if [ ! -d /home/ubuntu/aaho/stage ]; then
#		mkdir /home/ubuntu/aaho/stage
#	fi
#fi
#if [ "$DEPLOYMENT_GROUP_NAME" == "live" ]
#then
#	if [ ! -d /home/ubuntu/aaho/live ]; then
#		mkdir /home/ubuntu/aaho/live
#	fi
#fi
#if [ "$DEPLOYMENT_GROUP_NAME" == "stage" ]
#then
#	if [ ! -d /home/ubuntu/aaho/stage/web ]; then
#		mkdir /home/ubuntu/aaho/stage/web
#	else
#		rm -rf /home/ubuntu/aaho/stage/web/*
#	fi
#fi
#if [ "$DEPLOYMENT_GROUP_NAME" == "live" ]
#then
#	if [ ! -d /home/ubuntu/aaho/live/web ]; then
#		mkdir /home/ubuntu/aaho/live/web
#	else
#		rm -rf /home/ubuntu/aaho/live/web/*
#	fi
#fi
