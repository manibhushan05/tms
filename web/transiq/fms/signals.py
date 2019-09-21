# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.conf import settings
from googletrans import Translator
import datetime
from fms import tasks
from restapi.utils import AahoTranslator


def get_sms_template(instance, dest_lang, city_joiner, vehicle, rate_hindi, sales_user):
    from authentication.models import Profile
    translator = AahoTranslator()
    title = 'TransIQ Transport'
    if dest_lang == 'hi':
        try:
            from_city_msg_trans = instance.from_city.city_local.hindi_name
            to_city_msg_trans = instance.to_city.city_local.hindi_name
        except:
            from_city_msg_trans = instance.from_city.name
            to_city_msg_trans = instance.to_city.name
    else:
        from_city_msg_trans = instance.from_city.name
        to_city_msg_trans = instance.to_city.name

    city_join_msg = city_joiner
    # city_join_msg_trans = translator.translate(city_join_msg, src='en', dest=dest_lang)
    t_response = translator.translate(city_join_msg, src='en', dest=dest_lang)
    if t_response['status'] == 'success':
        city_join_msg_trans = t_response['text']
    else:
        city_join_msg_trans = 'to'
        from_city_msg_trans = instance.from_city.name
        to_city_msg_trans = instance.to_city.name
        rate_hindi = False
    to_state_msg = "({}) ".format(instance.to_city.state.name)
    # to_state_msg_trans = translator.translate(to_state_msg, dest=dest_lang)
    to_state_msg_trans = translator.translate(to_state_msg, dest=dest_lang)['text']
    date_msg = "Date: {}".format(
        datetime.datetime.strptime(instance.from_shipment_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
    # date_msg_trans = translator.translate(date_msg, src='en', dest=dest_lang)
    date_msg_trans = translator.translate(date_msg, src='en', dest=dest_lang)['text']

    fixed_template = title + '\n' + from_city_msg_trans + ' ' + city_join_msg_trans + ' ' + to_city_msg_trans \
                     + ' ' + to_state_msg_trans + '\n' + \
                     date_msg_trans + '\n'
    tonnage_msg = ''
    no_of_vehicles_msg = ''
    rate_msg = ''
    tonnage_msg_trans = ''
    no_of_vehicles_msg_trans = ''
    rate_msg_trans = ''
    vehicle_type_msg = ''
    remark_msg = ''
    if instance.type_of_vehicle:
        vehicle_type = vehicle + ": "
        # vehicle_type_msg_trans = translator.translate(vehicle_type, src='en', dest=dest_lang)
        t_response = translator.translate(vehicle_type, src='en', dest=dest_lang)
        if t_response['status'] == 'success':
            vehicle_type_msg_trans = t_response['text']
        else:
            vehicle_type_msg_trans = 'Vehicle: '
        vehicle_type_msg = vehicle_type_msg_trans + instance.type_of_vehicle.get_name() + '\n'
    if instance.tonnage:
        tonnage_msg = "Weight: {} ton \n".format(instance.tonnage)
        # tonnage_msg_trans = translator.translate(tonnage_msg, src='en', dest=dest_lang).text + '\n'
        tonnage_msg_trans = translator.translate(tonnage_msg, src='en', dest=dest_lang)['text'] + '\n'
    if instance.no_of_vehicles:
        no_of_vehicles_msg = "{}".format(instance.no_of_vehicles) + ' ' + vehicle + '\n'
        # no_of_vehicles_msg_trans = translator.translate(no_of_vehicles_msg, src='en', dest=dest_lang).text + '\n'
        t_response = translator.translate(no_of_vehicles_msg, src='en', dest=dest_lang)
        if t_response['status'] == 'success':
            no_of_vehicles_msg_trans = t_response['text'] + '\n'
        else:
            no_of_vehicles_msg_trans = "{}".format(instance.no_of_vehicles) + ' Vehicle\n'

    if instance.rate:
        if rate_hindi:
            rate_msg = "रेट: {}".format(instance.rate)
            # rate_m = rate_msg.decode('utf-8')
            rate_m = rate_msg
        else:
            rate_msg = "Rate: {}".format(instance.rate)
            # rate_msg_trans = translator.translate(rate_msg, src='en', dest=dest_lang)
            rate_msg_trans = translator.translate(rate_msg, src='en', dest=dest_lang)['text']
            rate_m = rate_msg_trans
    else:
        rate_m = ''
    if instance.remark:
        if instance.rate:
            remark_msg = "\n{}\n".format(instance.remark)
        else:
            remark_msg = "{}\n".format(instance.remark)

    sales_phone = None
    sales_name = None
    if sales_user:
        try:
            sales_profile = Profile.objects.get(user=sales_user)
        except Profile.DoesNotExist:
            sales_profile = None
        if sales_profile:
            sales_phone = sales_profile.phone
            sales_name = sales_profile.name

    if sales_phone and sales_name:
        call_two_phone = sales_phone
        call_two_name = sales_name
        call_two_msg = call_two_name + ' : ' + call_two_phone
    else:
        if instance.aaho_office.t2_phone:
            call_two_phone = instance.aaho_office.t2_phone
            if instance.aaho_office.t2_name:
                call_two_name = instance.aaho_office.t2_name
            else:
                call_two_name = ''
            call_two_msg = call_two_name + ' : ' + call_two_phone
        else:
            call_two_msg = ''

    if instance.aaho_office.t1_phone:
        call_one_phone = instance.aaho_office.t1_phone
        if instance.aaho_office.t1_name:
            call_one_name = instance.aaho_office.t1_name
        else:
            call_one_name = ''
        call_one_msg = call_one_name + ' : ' + call_one_phone
    else:
        call_one_msg = ''

    # if instance.aaho_office.t2_phone:
    #     call_two_phone = instance.aaho_office.t2_phone
    #     if instance.aaho_office.t2_name:
    #         call_two_name = instance.aaho_office.t2_name
    #     else:
    #         call_two_name = ''
    #     call_two_msg = call_two_name + ' : ' + call_two_phone
    # else:
    #     call_two_msg = ''

    call_msg = " Call : "
    # call_msg_trans = translator.translate(call_msg, src='en', dest=dest_lang)
    call_msg_trans = translator.translate(call_msg, src='en', dest=dest_lang)['text']
    final_template = fixed_template + vehicle_type_msg + tonnage_msg_trans + no_of_vehicles_msg_trans + \
                     rate_m + remark_msg + '\n' + call_msg_trans + '\n' + \
                     call_one_msg + '\n' + call_two_msg
    final_template = final_template.encode('utf-8')
    return final_template


def send_sms_to_supplier(instance, sales_user):
    from authentication.models import Profile
    if settings.TESTING:
        return
    mobiles_list = []
    if sales_user:
        try:
            sales_phone = Profile.objects.get(user=sales_user).phone
        except Profile.DoesNotExist:
            sales_phone = None
        if sales_phone:
            mobiles_list.append(sales_phone)

    traffic_users = User.objects.filter(employee__office_id=instance.aaho_office.id,
                                        employee__employee_role_mapping__employee_role__role='traffic')
    for traffic_user in traffic_users:
        try:
            traffic_phone = Profile.objects.get(user=traffic_user).phone
        except Profile.DoesNotExist:
            traffic_phone = None
        if traffic_phone:
            mobiles_list.append(traffic_phone)

    if instance.aaho_office.id == 3:
        # final_template_te = get_sms_template(instance, 'te', 'to', 'Vehicle', False)
        final_template_en = get_sms_template(instance, 'en', 'to', 'Vehicle', False, sales_user)
        final_template = final_template_en
    else:
        final_template = get_sms_template(instance, 'hi', 'from', 'cart', True, sales_user)
    req_dest_state = instance.to_city.state
    suppliers = instance.aaho_office.supplier_aaho_office.all()
    if suppliers:
        for supplier in suppliers:
            if supplier and supplier.id not in [635, 1601, 2680, 1835, 2145, 2740]:
                supplier_states = supplier.serving_states.all()
                if req_dest_state not in supplier_states:
                    continue
                if supplier.name not in mobiles_list:
                    if supplier.phone:
                        mobiles_list.append(supplier.phone)
        mobiles = ', '.join(mobiles_list)
        print(mobiles)
        # mobiles = '8451044751'
        if mobiles:
            tasks.send_sms_to_suppliers(mobiles, final_template)


def send_notification_to_sales(instance, created, lapsed_notification):
    from notification.models import MobileDevice
    print('Inside send_notification_to_sales')
    aaho_office_id = instance.aaho_office.id
    client_name = instance.client.name.profile.name
    if created:
        title = "New Load"
        body = "Requirement submitted by {}".format(client_name)
    else:
        title = "Load Updated"
        body = "Requirement updated by {}".format(client_name)
    notification_users = User.objects.filter(employee__office_id=aaho_office_id,
                                             employee__employee_role_mapping__employee_role__role='sales')
    client_device = None
    if lapsed_notification:
        client_user = instance.client.name
        client_device = MobileDevice.objects.filter(user=client_user)
        title = "Load Lapsed"
        body = "Requirement by {} Lapsed".format(client_name)
    q_objects = Q()
    q_objects |= Q(**{'app': 'AS'})
    q_objects |= Q(**{'app': 'AE'})
    mobile_device = MobileDevice.objects.filter(q_objects)
    mobile_device = mobile_device.filter(user__in=notification_users)
    if client_device:
        mobile_device = mobile_device.union(client_device)
    if not mobile_device:
        print("Device not found")
        return
    mobile_device = list(mobile_device.values_list('id', flat=True))
    tasks.send_app_notification.delay(mobile_device, title, body)


def send_notification_to_traffic(instance):
    from notification.models import MobileDevice
    print('Inside send_notification_to_traffic')
    title = "New Load"
    body = "Requirement submitted for {} to {}".format(instance.from_city.name, instance.to_city.name)
    traffic_users = User.objects.filter(employee__office_id=instance.aaho_office.id,
                                        employee__employee_role_mapping__employee_role__role='traffic')

    mobile_device = MobileDevice.objects.filter(user__in=traffic_users)
    if not mobile_device:
        print("Device not found")
        return
    data = {'title': title, 'body': body}
    mobile_device = list(mobile_device.values_list('id', flat=True))
    tasks.send_app_notification.delay(mobile_device, title, body, data)


def send_notification_to_brokers(instance):
    from notification.models import MobileDevice
    title = "New Load"
    body = "Requirement submitted for {} to {}".format(instance.from_city.name, instance.to_city.name)
    suppliers = instance.aaho_office.supplier_aaho_office.all()
    req_dest_state = instance.to_city.state
    supplier_user_list = []
    if suppliers:
        for supplier in suppliers:
            if supplier:
                supplier_states = supplier.serving_states.all()
                if req_dest_state not in supplier_states:
                    continue
                supplier_user_list.append(supplier.user)

    mobile_device = MobileDevice.objects.filter(user__in=supplier_user_list)
    if not mobile_device:
        print("Device not found")
        return
    data = {'title': title, 'body': body}
    mobile_device = list(mobile_device.values_list('id', flat=True))
    tasks.send_app_notification.delay(mobile_device, title, body, data)


def requirement_post_save_handler(sender, instance, created, **kwargs):
    print("Created: ", created)
    if created:
        if instance.req_status == 'open':
            print('new req sending sms')
            send_sms_to_supplier(instance, instance.created_by)
            send_notification_to_brokers(instance)
            send_notification_to_traffic(instance)
        else:
            print('new req sending notification')
            send_notification_to_sales(instance, created, False)
    else:
        if kwargs['update_fields'] and 'deleted' not in kwargs['update_fields']:
            if instance.req_status == 'open':
                print('update verified sending sms')
                send_sms_to_supplier(instance, instance.changed_by)
                send_notification_to_brokers(instance)
            if instance.req_status == 'lapsed':
                print('load lapsed sending notification to sales and customer')
                send_notification_to_sales(instance, created, True)
            # if 'req_status' in kwargs['update_fields']:
            #     print('update verified sending sms')
            #     send_sms_to_supplier(instance)
        else:
            print('customer update sending notification')
            send_notification_to_sales(instance, created, False)
