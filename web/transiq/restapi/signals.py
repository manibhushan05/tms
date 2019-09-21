from django.conf import settings

from fms import tasks
from restapi.helper_api import get_td_functionality_notification_users, get_td_functionality_roles_notification_users


def create_booking_status_mapping_comments(instance, comment):
    from restapi.serializers.task_dashboard import BookingStatusesMappingCommentsSerializer
    data = dict()
    data["created_by"] = instance.created_by
    data["booking_status_mapping_id"] = instance.id
    data["comment"] = comment
    booking_statuses_mapping_comments_serializer = BookingStatusesMappingCommentsSerializer(data=data)
    if booking_statuses_mapping_comments_serializer.is_valid():
        booking_statuses_mapping_comments_serializer.save()
        print("Booking Status Mapping Comment Created")
    else:
        print("Booking Status Mapping Comment Not Created: ", booking_statuses_mapping_comments_serializer.errors)
    return


def send_booking_status_expired_notification(notification_data):
    for nd in notification_data:
        notification_users = get_td_functionality_notification_users(nd['functionality'], nd['aaho_office_id'], nd['app'])
        if not notification_users:
            print("Device not found")
            return
        title = "Booking pending for " + nd['title_text']
        body = "Booking ID {} is pending for {}".format(nd['booking_id'], nd['title_text'])
        data = {'title': title, 'body': body, 'functionality': nd['functionality'],
                'booking_id': nd['booking_id'], 'notification_count': 1, 'is_count_update': nd['is_count_update']}
        tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_inward_entry_personnel(instance):
    notification_users = get_td_functionality_notification_users('inward_entry',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Inward Followed Up"
    body = "Booking ID {} is ready for Inward Settlement".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'inward_entry',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_inward_followup_personnel(instance):
    notification_users = get_td_functionality_notification_users('pending_payments',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'AE')
    if not notification_users:
        print("Device not found")
        return
    title = "Invoice Confirmed"
    body = "Booking ID {} is ready for Inward Followup".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'pending_payments',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_invoice_confirmed_personnel(instance):
    notification_users = get_td_functionality_notification_users('confirm_invoice',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Invoice Sent"
    body = "Booking ID {} is ready for Confirming Invoice".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'confirm_invoice',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_party_invoice_sent_personnel(instance):
    notification_users = get_td_functionality_notification_users('send_invoice',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Invoice Raised"
    body = "Booking ID {} is ready for Sending Invoice".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'send_invoice',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_raise_invoice_personnel(instance):
    notification_users = get_td_functionality_notification_users('raise_invoice',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "PoD Verified"
    body = "Booking ID {} is ready for Raising Invoice".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'raise_invoice',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_pod_verify_personnel(instance):
    notification_users = get_td_functionality_notification_users('verify_pod',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "PoD Uploaded"
    body = "Booking ID {} is ready for PoD verification".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'verify_pod',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_invoice_confirmed_escalated_personnel(sme, aaho_office_id, invoice_number):
    notification_users = get_td_functionality_roles_notification_users('invoice_confirmation',
                                                                       aaho_office_id,
                                                                       'AE',
                                                                       'sales')
    notification_users = notification_users.filter(user=sme.aaho_poc.username)
    if not notification_users:
        print("Device not found")
        return
    title = "Escalated"

    body = "Invoice ID {} {}".format(invoice_number, title)
    data = {'title': title, 'body': body, 'functionality': 'invoice_confirmation',
            'booking_id': invoice_number, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_delivered_pod_update_personnel(instance):
    notification_users = get_td_functionality_roles_notification_users('delivered',
                                                                       instance.manual_booking.destination_office.id,
                                                                       'AE',
                                                                       'sales')
    if not notification_users:
        print("Device not found")
        return
    if instance.booking_stage == 'in_progress':
        title = "PoD Uploaded"
    elif instance.booking_stage == 'escalated':
        title = "PoD Escalated"
    elif instance.booking_stage == 'reverted':
        title = "PoD Rejected"
    else:
        title = "PoD"
    body = "Booking ID {} {}".format(instance.manual_booking.booking_id, title)
    data = {'title': title, 'body': body, 'functionality': 'delivered',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_delivered_personnel(instance):
    notification_users = get_td_functionality_notification_users('delivered',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'AE')
    if not notification_users:
        print("Device not found")
        return
    title = "Delivered"
    body = "Booking ID {} is Delivered".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'delivered',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_in_transit_personnel(instance):
    notification_users = get_td_functionality_notification_users('in_transit',
                                                                 instance.manual_booking.destination_office.id,
                                                                 'AE')
    if not notification_users:
        print("Device not found")
        return
    title = "In Transit"
    body = "Booking ID {} is in Transit".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'in_transit',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_advance_paid_personnel(instance):
    notification_users = get_td_functionality_notification_users('pay_advance',
                                                                 instance.manual_booking.source_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Pay Advance"
    body = "Booking ID {} is ready for Pay Advance".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'pay_advance',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_reconcile_personnel(instance):
    notification_users = get_td_functionality_notification_users('reconcile',
                                                                 instance.manual_booking.source_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Reconcile"
    body = "Booking ID {} is ready for Reconcile".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'reconcile',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)
    return


def send_notification_to_lr_generation_personnel(instance):
    notification_users = get_td_functionality_notification_users('lr_generation',
                                                                 instance.manual_booking.source_office.id,
                                                                 'WB')
    if not notification_users:
        print("Device not found")
        return
    title = "Generate LR"
    body = "Booking ID {} is ready for LR".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'lr_generation',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)


def send_notification_to_pending_lr_personnel(instance):
    notification_users = get_td_functionality_notification_users(
        'pending_lr', instance.manual_booking.source_office.id, 'AE')
    if not notification_users:
        print("Device not found")
        return
    title = "New Booking Confirmed"
    body = "Booking ID {} is Created".format(instance.manual_booking.booking_id)
    data = {'title': title, 'body': body, 'functionality': 'pending_lr',
            'booking_id': instance.manual_booking.booking_id, 'notification_count': 1, 'is_count_update': True}
    tasks.send_app_notification.delay(notification_users, title, body, data)


def booking_status_mapping_post_save_handler(sender, instance, created, **kwargs):
    if settings.TESTING or not settings.ENABLE_CELERY:
        return
    if created:
        bss = BookingStatusSwitcher(instance)
        bss.case(instance.booking_status_chain.booking_status.status)
        return 0
    elif instance.booking_status_chain.booking_status.status == 'pod_uploaded':
        print('Booking PoD '+instance.booking_stage)
        send_notification_to_delivered_pod_update_personnel(instance)


class BookingStatusSwitcher(object):
    def __init__(self, booking_instance):
        self.booking_instance = booking_instance

    def case(self, key):
        method_name = 'booking_status_' + str(key)
        method = getattr(self, method_name, lambda: 'Invalid Booking Status')
        return method()

    def booking_status_confirmed(self):
        print('Booking confirmed')
        send_notification_to_pending_lr_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'booking confirmed')
        return

    def booking_status_loaded(self):
        print('Booking loaded')
        send_notification_to_lr_generation_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'loaded')
        return

    def booking_status_lr_generated(self):
        print('Booking LR Generated')
        send_notification_to_advance_paid_personnel(self.booking_instance)
        send_notification_to_in_transit_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'LR Generated')
        return

    def booking_status_advance_paid(self):
        print('Booking Advance Paid')
        # send_notification_to_reconcile_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Advance Paid')
        return

    def booking_status_unloaded(self):
        print('Booking Unloaded')
        send_notification_to_delivered_personnel(self.booking_instance)
        # send_notification_to_invoice_raised_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Delivered')
        return

    def booking_status_pod_uploaded(self):
        print('Booking PoD Uploaded')
        send_notification_to_pod_verify_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'PoD Uploaded')
        return

    def booking_status_pod_verified(self):
        print('Booking PoD Verified')
        # send_notification_to_balance_payment_personnel(self.booking_instance)
        send_notification_to_raise_invoice_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'PoD Verified')
        return

    def booking_status_invoice_raised(self):
        print('Booking Invoice Raised')
        send_notification_to_party_invoice_sent_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Invoice Raised')
        return

    def booking_status_invoice_confirmed(self):
        print('Booking Invoice Confirmed')
        send_notification_to_inward_followup_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Invoice Confirmed')
        return

    def booking_status_balance_paid(self):
        print('Booking Balance Paid')
        # send_notification_to_reconcile_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Balance Paid')
        return

    def booking_status_party_invoice_sent(self):
        print('Booking Party Invoice Sent')
        send_notification_to_invoice_confirmed_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Party Invoice Sent')
        return

    def booking_status_inward_followup_completed(self):
        print('Booking Inward Followup Completed')
        send_notification_to_inward_entry_personnel(self.booking_instance)
        create_booking_status_mapping_comments(self.booking_instance, 'Inward Followup Completed')
        return

    def booking_status_complete(self):
        print('Booking Complete')
        create_booking_status_mapping_comments(self.booking_instance, 'Complete')
        return
