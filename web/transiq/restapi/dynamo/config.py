from django.conf import settings
from restapi.dynamo.models import DEV_GPS_LOCATION, STAGE_GPS_LOCATION, PROD_GPS_LOCATION, LOCAL_GPS_LOCATION, DEV_User, \
    STAGE_User, PROD_User, LOCAL_User


class DynamoTablesEnvConfiguration:
    def __init__(self):
        if settings.ENV == 'dev':
            self.GPS_LOCATION = DEV_GPS_LOCATION
            self.User = DEV_User
        elif settings.ENV == 'stage':
            self.GPS_LOCATION = STAGE_GPS_LOCATION
            self.User = STAGE_User
        elif settings.ENV == 'prod':
            self.GPS_LOCATION = PROD_GPS_LOCATION
            self.User = PROD_User
        else:
            self.GPS_LOCATION = LOCAL_GPS_LOCATION
            self.User = LOCAL_User
