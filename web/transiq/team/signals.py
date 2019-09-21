from django.db.models.signals import post_save
from django.dispatch import receiver

from api.utils import get_or_none
from team.models import ManualBooking, BookingStatusColor


@receiver(post_save, sender=ManualBooking)
def save_booking_color_code(sender, instance=None, created=False, **kwargs):
    if instance.total_amount_to_company == 0:
        color_code = get_or_none(BookingStatusColor, keyword='zblue')
    elif instance.balance_for_customer <= 0:
        color_code = get_or_none(BookingStatusColor, keyword='zgreen')
    elif instance.pod_status == 'completed' and instance.invoice_status == 'no_invoice':
        color_code = get_or_none(BookingStatusColor, keyword='zorange')
    elif instance.pod_status == 'completed' and instance.invoice_status == 'invoice_raised':
        color_code = get_or_none(BookingStatusColor, keyword='zpurple')
    elif instance.pod_status == 'completed' and instance.invoice_status == 'invoice_sent':
        color_code = get_or_none(BookingStatusColor, keyword='zpurple')
    elif instance.pod_status != 'completed':
        color_code = get_or_none(BookingStatusColor, keyword='zred')
    else:
        color_code = get_or_none(BookingStatusColor, keyword='zblack')
