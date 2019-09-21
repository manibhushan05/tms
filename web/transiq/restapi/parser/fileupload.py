import json
from datetime import datetime
from api.utils import get_or_none
from restapi.helper_api import generate_random_string
from team.models import LrNumber, ManualBooking


def parse_pod_upload_fms(data):
    if isinstance(data['podData'], list):
        pod_json_array = data['podData']
    else:
        pod_json_array = json.loads(data['podData'])
    booking = get_or_none(ManualBooking, booking_id=data['lr_number'])
    if isinstance(booking, ManualBooking):
        booking = booking.id
        lr_number = None
    else:
        lr_number = get_or_none(LrNumber, lr_number=data.get('lr_number', None))
        booking = lr_number.booking.id if isinstance(lr_number.booking, ManualBooking) else None
        lr_number=lr_number.id if isinstance(lr_number,LrNumber) else None
    pod_data = []
    for pod in pod_json_array:
        pod_data.append({
            'booking': booking,
            'lr_number': lr_number,
            's3_url': pod.get('url',None),
            's3_thumb_url': pod.get('thumbUrl',None),
            'created_by': data.get('user',None),
            'changed_by': data.get('user',None),
            'uploaded_by': data.get('user',None),
            'serial': generate_random_string(N=20),
            's3_upload_data': {
                'bucket': pod.get('bucketname', None),
                'filename': pod.get('filename', None),
                'folder': pod.get('foldername', None),
                'uuid': pod.get('uuid', None),
                'uploaded': True,
                'verified': False,
                'is_valid': False,
                'uploaded_on': datetime.now(),
            }
        })
    return pod_data
