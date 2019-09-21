#!/bin/bash -e

if [ "$DEPLOYMENT_GROUP_NAME" == "stage" ]
then
	cd /home/ubuntu/aaho/web/config/ci/common/ && chmod u+x *.sh && chmod u+x ../stage/settings.sh && ./config.sh stage
fi
if [ "$DEPLOYMENT_GROUP_NAME" == "live" ]
then
	cd /home/ubuntu/aaho/web/config/ci/common/ && chmod u+x *.sh && chmod u+x ../prod/settings.sh && ./config.sh prod
fi
