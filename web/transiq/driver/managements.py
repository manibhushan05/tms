from datetime import datetime, timedelta
from io import BytesIO

from django.utils.text import slugify
from api.s3util import save_to_s3_gps_log
from driver.models import TracknovateGPSDeviceLog, TempoGoGPSDeviceLog, WaytrackerGPSDeviceLog, \
    SecuGPSDeviceLog, MahindraGPSDeviceLog
import pandas as pd

from owner.models import Vehicle


def download_tracknovate_gps_log():
    data = [[log.datetime, log.vehicle_id, log.latitude, log.longitude]
            for log in TracknovateGPSDeviceLog.objects.all()]
    df = pd.DataFrame(data=data, columns=['Datetime', 'Vehicle ID', 'Latitude', 'Longitude'])
    df.to_excel('/Users/mani/workspace/aaho/data/tracknovate.xlsx', index=False)


def history_test():
    device = Vehicle.objects.get(id=3073)
    h = device.history.all()
    for value in h:
        print(value.owner, value.history_date, value.history_user, value.get_history_type_display())


def delete_tempogo_data():
    device_ids = TempoGoGPSDeviceLog.objects.values_list('device_id', flat=True).distinct()
    data = []
    for device in device_ids:
        last_data = TempoGoGPSDeviceLog.objects.filter(
            device__id=device, datetime__lte=(datetime.now() - timedelta(days=15)).date()).last()
        if last_data:
            data.append(last_data.id)
    gps_data = []
    for gps in TempoGoGPSDeviceLog.objects.exclude(id__in=data):
        gps_data.append([
            gps.id,
            gps.device.device_id if gps.device else '',
            gps.created_on.strftime('%d-%b-%Y %H:%M:%S'),
            gps.updated_on.strftime('%d-%b-%Y %H:%M:%S'),
            gps.datetime.strftime('%d-%b-%Y %H:%M:%S'),
            gps.gps_log_id,
            gps.latitude,
            gps.longitude,
            gps.speed,
            gps.driver_name,
            gps.driver_number,
            gps.driving_licence_number,
            gps.vehicle_number,
            gps.vehicle_type,
            gps.vehicle_status
        ])
    df = pd.DataFrame(
        data=gps_data,
        columns=['ID', 'Device ID', 'Created on', 'Updated on', 'GPS Log time', 'GPS Log id', 'Latitude', 'Longitude',
                 'Speed', 'Driver name', 'Driver Number', 'DL Number', 'Vehicle Number', 'Vehicle Type',
                 'Vehicle Status']
    )
    bytes_io = BytesIO()
    df.to_csv(bytes_io, index=False)
    bytes_io.seek(0)
    content = bytes_io.getvalue() or '\n'
    filename = '{}.{}'.format(slugify('TempoGo GPS log Data {}'.format(datetime.now().strftime('%d %b %Y %I %M %S'))),
                              'csv')
    df.to_csv(filename, index=False)
    save_to_s3_gps_log(filename, content)
    TempoGoGPSDeviceLog.objects.exclude(id__in=data).delete()


def delete_waytracker_gps_log():
    device_ids = WaytrackerGPSDeviceLog.objects.values_list('device_id', flat=True).distinct()
    data = []
    for device in device_ids:
        last_data = WaytrackerGPSDeviceLog.objects.filter(
            device__id=device, datetime__lte=(datetime.now() - timedelta(days=7)).date()).last()

        if last_data:
            data.append(last_data.id)
    # gps_data = []
    # for gps in WaytrackerGPSDeviceLog.objects.exclude(id__in=data):
    #     gps_data.append([
    #         gps.id,
    #         gps.device.vehicle_id if gps.device else '',
    #         gps.created_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.updated_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.datetime.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.latitude,
    #         gps.longitude,
    #         gps.speed,
    #         gps.driver_name,
    #         gps.driver_number,
    #         gps.driving_licence_number,
    #         gps.vehicle_number,
    #         gps.vehicle_type,
    #         gps.vehicle_status
    #     ])
    #     print(gps)
    # df = pd.DataFrame(
    #     data=gps_data,
    #     columns=['ID', 'Device ID', 'Created on', 'Updated on', 'GPS Log time', 'Latitude', 'Longitude',
    #              'Speed', 'Driver name', 'Driver Number', 'DL Number', 'Vehicle Number', 'Vehicle Type',
    #              'Vehicle Status']
    # )
    # bytes_io = BytesIO()
    # df.to_csv(bytes_io, index=False)
    # bytes_io.seek(0)
    # content = bytes_io.getvalue() or '\n'
    # filename = '{}.{}'.format(
    #     slugify('WayTracker GPS log Data {}'.format(datetime.now().strftime('%d %b %Y %I %M %S'))), 'csv')
    # df.to_csv(filename, index=False)
    # save_to_s3_gps_log(filename, content)
    WaytrackerGPSDeviceLog.objects.exclude(id__in=data).delete()


def delete_secugps_gps_log():
    device_ids = SecuGPSDeviceLog.objects.values_list('device_id', flat=True).distinct()
    data = []
    for device in device_ids:
        last_data = SecuGPSDeviceLog.objects.filter(
            device__id=device, datetime__lte=(datetime.now() - timedelta(days=9)).date()).last()

        if last_data:
            data.append(last_data.id)
    # gps_data = []
    # for gps in SecuGPSDeviceLog.objects.exclude(id__in=data):
    #     gps_data.append([
    #         gps.id,
    #         gps.device.device_id if gps.device else '',
    #         gps.created_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.updated_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.datetime.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.latitude,
    #         gps.longitude,
    #         gps.speed,
    #         gps.driver_name,
    #         gps.driver_number,
    #         gps.driving_licence_number,
    #         gps.vehicle_number,
    #         gps.vehicle_type,
    #         gps.vehicle_status
    #     ])
    #     print(gps)
    # df = pd.DataFrame(
    #     data=gps_data,
    #     columns=['ID', 'Device ID', 'Created on', 'Updated on', 'GPS Log time', 'Latitude', 'Longitude',
    #              'Speed', 'Driver name', 'Driver Number', 'DL Number', 'Vehicle Number', 'Vehicle Type',
    #              'Vehicle Status']
    # )
    # bytes_io = BytesIO()
    # df.to_csv(bytes_io, index=False)
    # bytes_io.seek(0)
    # content = bytes_io.getvalue() or '\n'
    # filename = '{}.{}'.format(
    #     slugify('SecuGPSDevice GPS log Data {}'.format(datetime.now().strftime('%d %b %Y %I %M %S'))), 'csv')
    # df.to_csv(filename, index=False)
    # save_to_s3_gps_log(filename, content)
    SecuGPSDeviceLog.objects.exclude(id__in=data).delete()


def delete_mahindra_gps_log():
    device_ids = MahindraGPSDeviceLog.objects.values_list('device_id', flat=True).distinct()
    data = []
    for device in device_ids:
        last_data = MahindraGPSDeviceLog.objects.filter(
            device__id=device, datetime__lte=(datetime.now() - timedelta(days=9)).date()).last()

        if last_data:
            data.append(last_data.id)
    gps_data = []
    # for gps in MahindraGPSDeviceLog.objects.exclude(id__in=data):
    #     gps_data.append([
    #         gps.id,
    #         gps.device.device_id if gps.device else '',
    #         gps.created_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.updated_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.datetime.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.latitude,
    #         gps.longitude,
    #         gps.speed,
    #         gps.driver_name,
    #         gps.driver_number,
    #         gps.driving_licence_number,
    #         gps.vehicle_number,
    #         gps.vehicle_type,
    #         gps.vehicle_status
    #     ])
    #     print(gps)
    # df = pd.DataFrame(
    #     data=gps_data,
    #     columns=['ID', 'Device ID', 'Created on', 'Updated on', 'GPS Log time', 'Latitude', 'Longitude',
    #              'Speed', 'Driver name', 'Driver Number', 'DL Number', 'Vehicle Number', 'Vehicle Type',
    #              'Vehicle Status']
    # )
    # bytes_io = BytesIO()
    # df.to_csv(bytes_io, index=False)
    # bytes_io.seek(0)
    # content = bytes_io.getvalue() or '\n'
    # filename = '{}.{}'.format(
    #     slugify('Mahindra GPS log Data {}'.format(datetime.now().strftime('%d %b %Y %I %M %S'))), 'csv')
    # df.to_csv(filename, index=False)
    # save_to_s3_gps_log(filename, content)
    MahindraGPSDeviceLog.objects.exclude(id__in=data).delete()


def delete_trackovate_gps_log():
    device_ids = TracknovateGPSDeviceLog.objects.values_list('device_id', flat=True).distinct()
    data = []
    for device in device_ids:
        last_data = TracknovateGPSDeviceLog.objects.filter(
            device__id=device, datetime__lte=(datetime.now() - timedelta(days=9)).date()).last()

        if last_data:
            data.append(last_data.id)
    # gps_data = []
    # for gps in TracknovateGPSDeviceLog.objects.exclude(id__in=data):
    #     gps_data.append([
    #         gps.id,
    #         gps.device.vehicle_id if gps.device else '',
    #         gps.created_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.updated_on.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.datetime.strftime('%d-%b-%Y %H:%M:%S'),
    #         gps.latitude,
    #         gps.longitude,
    #         gps.speed,
    #         gps.driver_name,
    #         gps.driver_number,
    #         gps.driving_licence_number,
    #         gps.vehicle_number,
    #         gps.vehicle_type,
    #         gps.vehicle_status
    #     ])
    #     print(gps)
    # df = pd.DataFrame(
    #     data=gps_data,
    #     columns=['ID', 'Device ID', 'Created on', 'Updated on', 'GPS Log time', 'Latitude', 'Longitude',
    #              'Speed', 'Driver name', 'Driver Number', 'DL Number', 'Vehicle Number', 'Vehicle Type',
    #              'Vehicle Status']
    # )
    # bytes_io = BytesIO()
    # df.to_csv(bytes_io, index=False)
    # bytes_io.seek(0)
    # content = bytes_io.getvalue() or '\n'
    # filename = '{}.{}'.format(
    #     slugify('Tracknovate GPS log Data {}'.format(datetime.now().strftime('%d %b %Y %I %M %S'))), 'csv')
    # df.to_csv(filename, index=False)
    # save_to_s3_gps_log(filename, content)
    TracknovateGPSDeviceLog.objects.exclude(id__in=data).delete()
