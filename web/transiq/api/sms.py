import requests
from django.conf import settings

from api.models import FakeSms


def send_sms(mobiles, message):
    authkey = "115151AKpRGb9tug57565bd3"  # Your authentication key.
    # mobiles = "8978937498,9324799518" # Multiple mobiles numbers separated by comma.
    # message = "TEST MSG \nRegards,\nMani Bhushan" # Your message to send.
    sender = "AAHOTP"  # Sender ID,While using route4 sender id should be 6 characters long.
    route = 4  # Define route
    # Prepare you post parameters
    if not settings.ENABLE_SMS and not settings.TESTING:
        # FakeSms.send(numbers=mobiles, text=message)
        mobiles = '9619125174'
        return
    values = {
        'authkey': authkey,
        'mobiles': mobiles,
        'message': message,
        'sender': sender,
        'route': route,
        'response': 'json',
        'unicode': 1
    }
    print(values)
    url = "https://control.msg91.com/api/sendhttp.php"  # API URL

    postdata = requests.post(url=url, data=values)  # URL encoding the data here.
    print(postdata.content)


def holi_wish_message_supplier():
    from supplier.models import Supplier, Driver

    message = 'Happy Holi to you and your family.\nHave a great year ahead\n\nTrans IQ transport\nAaho logistics'
    hi_msg=u'आपको और आपके परिवार को होली की हार्दिक शुभकामनाएँ। हम आपके स्वास्थ्य, समृद्धि और व्यावसायिक उपलब्धियों की कामना करते हैं।\n\nट्रांस आईक्यू ट्रांसपोर्ट\nआहो लोजिस्टिक्स'
    mob=[]
    for supplier in Supplier.objects.exclude(deleted=True):
        if supplier.phone:
            mob.append(supplier.phone)
    for driver in Driver.objects.exclude(deleted=True):
        if driver.phone:
            mob.append(driver.phone)
    mobiles=','.join(list(set(mob)))
    print(mobiles)
    # mobiles='8978937498'
    send_sms(mobiles=mobiles,message=hi_msg)


def send_otp(mobiles, message):
    authkey = "115151AKpRGb9tug57565bd3"  # Your authentication key.
    # mobiles = "8978937498,9324799518" # Multiple mobiles numbers separated by comma.
    # message = "TEST MSG \nRegards,\nMani Bhushan" # Your message to send.
    sender = "AAHOTP"  # Sender ID,While using route4 sender id should be 6 characters long.
    route = 4  # Define route
    # Prepare you post parameters
    values = {
        'authkey': authkey,
        'mobiles': mobiles,
        'message': message,
        'sender': sender,
        'otp_length': 6,
        'response': 'json',
        'unicode': 1
    }
    url = "https://control.msg91.com/api/sendhttp.php"  # API URL
    if not settings.ENABLE_SMS:
        FakeSms.send(numbers=mobiles, text=message)
        return
    postdata = requests.post(url=url, data=values)  # URL encoding the data here.
