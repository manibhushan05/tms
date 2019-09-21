# from __future__ import unicode_literals
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.db.models import Q

from team.models import LrNumber
from owner.vehicle_util import display_format


def delayed_pod_warning_message(lr_number, shipment_date, vehicle_number, language='hindi'):
    if language == 'hindi':
        return (
            u'%s को Trans IQ (Aaho Logistics) के लिए वाहन नंबर %s जिसका बिल्टी न. %s है, लगाने के लिए धन्यवाद। इस माल की ‘पहुंच’ अभी तक प्राप्त नहीं हुई हैं। डिलीवरी के 10 दिनों बाद भी पहुंच प्राप्त नहीं होने पर प्रतिदिन 50 रुपये की कटौती लागू की जायेगी।' % (
                shipment_date, display_format(vehicle_number), lr_number)).encode('utf-8')
    elif language == 'telgu':
        return u''


def send_pod_sms():
    lr_numbers = LrNumber.objects.filter(booking__shipment_date__in=[
        datetime.today() - timedelta(days=5),
        datetime.today() - timedelta(days=10),
        datetime.today() - timedelta(days=15)
    ]).exclude(
        Q(booking__pod_status='completed') | (
        Q(booking__source_office_id__in=[2, 3]) | Q(booking__destination_office_id__in=[2, 3])))
    for lr in lr_numbers:
        print (lr.booking.shipment_date, lr.booking.truck_broker_owner_phone, lr.booking.source_office)
        # msg = delayed_pod_warning_sms(
        #     lr_number=lr.lr_number,
        #     shipment_date=lr.booking.shipment_date.strftime('%d-%b'),
        #     vehicle_number=lr.booking.lorry_number
        # )

        # print (msg,lr)
        # send_sms(mobiles='8978937498', message=msg)
