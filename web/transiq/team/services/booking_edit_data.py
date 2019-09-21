from team.models import ManualBooking
from utils.models import VehicleCategory


def get_full_booking_data(booking_id):
    mb = ManualBooking.objects.get(id=booking_id)
    deductions = int(
        mb.commission + mb.lr_cost + mb.deduction_for_advance + mb.deduction_for_balance + mb.other_deduction)
    booking_data = {
        'lr_number': ', '.join(mb.lr_numbers.values_list('lr_number', flat=True)),
        'freight_from_company': int(mb.charged_weight * mb.party_rate),
        'freight_from_owner': int(mb.supplier_charged_weight * mb.supplier_rate),
        'total_amount_from_company': int(
            mb.charged_weight * mb.party_rate) + mb.additional_charges_for_company - deductions,
        'total_amount_from_owner': int(
            mb.supplier_charged_weight * mb.supplier_rate) + mb.additional_charges_for_owner - deductions,
        'truck_type': VehicleCategory.objects.all()
    }
    return booking_data
