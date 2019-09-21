from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from datetime import datetime
from restapi.dynamo.config import DynamoTablesEnvConfiguration
from restapi.dynamo.gps_serialiser import GPSDeviceSerializers
from restapi.dynamo.utils import DynamoTable


class DynamoGPSDeviceListView(generics.ListAPIView):

    def list(self, request, *args, **kwargs):
        pass


class DynamoGPSDeviceViewSet(viewsets.ViewSet):
    """
        API for creation, updation, retrieval of NoSQL GPS Device
    """

    def create_table(self, request):
        """
            Creates the table if it does not exist.
        """
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        res = gps_dt.create()
        if res == -1:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "GPS Device Table already exist",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "status_code": status.HTTP_201_CREATED,
                "status": "success",
                "msg": "GPS Device Table Created",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_201_CREATED)

    def create_item(self, request):
        """
            Creates the table if it does not exist and adds an item.
        """
        request.data["created_by"] = self.request.user.username
        # request.data["changed_by"] = self.request.user.username
        gps_device_serializer = GPSDeviceSerializers(data=request.data)
        if gps_device_serializer.is_valid():
            if gps_device_serializer.save():
                response = {
                    "status_code": status.HTTP_201_CREATED,
                    "status": "success",
                    "msg": "Dynamo GPS Device Item Created",
                    "data": gps_device_serializer.data
                }
                return Response(data=response, status=status.HTTP_201_CREATED)

            else:
                response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "status": "failure",
                    "msg": "Dynamo GPS Device Item not Created",
                    "data": {}
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "GPS Device not Created",
                "data": gps_device_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        item = gps_dt.get_item(pk)

        if self.request.content_type != 'application/json':
            response = {"status": "failure", "msg": "Wrong Content Type. Must be application/json",
                        "data": {"GPS Device": {}}}
            return Response(response, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

        if item:
            gps_device_serializer = GPSDeviceSerializers(item)
            response = {
                "status_code": status.HTTP_200_OK,
                "status": "success",
                "msg": "Dynamo GPS Device Item Retrieved",
                "data": gps_device_serializer.data
            }
            return Response(data=response, status=status.HTTP_200_OK)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "Dynamo GPS Device Item Not Found",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        item = gps_dt.get_item(pk)
        if not item:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "Device id {} does not exists".format(pk),
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)

        request.data["changed_by"] = self.request.user.username
        gps_device_serializer = GPSDeviceSerializers(instance=item, data=request.data)
        if gps_device_serializer.is_valid():
            if gps_device_serializer.save():
                response = {
                    "status_code": status.HTTP_202_ACCEPTED,
                    "status": "success",
                    "msg": "Dynamo GPS Device Item Updated",
                    "data": gps_device_serializer.data
                }
                return Response(data=response, status=status.HTTP_202_ACCEPTED)

            else:
                response = {
                    "status_code": status.HTTP_400_BAD_REQUEST,
                    "status": "failure",
                    "msg": "Dynamo GPS Device Item not Updated",
                    "data": {}
                }
                return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "GPS Device not Updated",
                "data": gps_device_serializer.errors
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, pk=None):
        dtc = DynamoTablesEnvConfiguration()
        gps_dt = DynamoTable(dtc.GPS_LOCATION)
        item = gps_dt.get_item(pk)
        if item:
            attributes = {
                'changed_by': self.request.user.username,
                'deleted': True,
                'deleted_on': datetime.now()
            }
            gps_dt.update_item(item.device_id, attributes)
            response = {'status': 'success', 'msg': 'Dynamo GPS Device Item Deleted', 'data':
                {'id': item.device_id}, 'status_code': status.HTTP_200_OK}
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "status": "failure",
                "msg": "GPS Device not Found",
                "data": {}
            }
            return Response(data=response, status=status.HTTP_400_BAD_REQUEST)
        return Response(response, status=status.HTTP_200_OK)

