from team.models import ManualBooking
from utils.models import AahoOffice


def supplier_deductions(freight_to_owner, company_code, gst_liability, supplier, source_office, destination_office):
    source_office_id = None if not isinstance(source_office, AahoOffice) else source_office.id
    destination_office_id = None if not isinstance(destination_office, AahoOffice) else destination_office.id
    if source_office_id == 2 and destination_office_id == 3:
        if gst_liability != 'exempted':
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier).exclude(
                    gst_liability='exempted').latest('created_on')
            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 200,
                    'editable': True
                },
            }
        elif company_code in ['JSM', 'CNS']:
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier, company_code=company_code,
                    gst_liability='exempted').latest('created_on')
            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        else:
            try:
                booking = ManualBooking.objects.filter(
                    source_office_id=2, destination_office_id=3, supplier=supplier, gst_liability='exempted').latest(
                    'created_on')

            except ManualBooking.DoesNotExist:
                booking = None

            data = {
                'commission': {
                    'amount': booking.commission if booking else 0,
                    'editable': True if booking else True
                },
                'lr_cost': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 350,
                    'editable': True
                },
            }
    elif source_office_id == 2 and destination_office_id == 1:
        data = {
            'commission': {
                'amount': 1000,
                'editable': True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            },
        }
    elif source_office_id == 2:
        try:
            booking = ManualBooking.objects.filter(
                source_office_id=2, destination_office_id=destination_office.id, supplier=supplier
            ).exclude(destination_office_id__in=[1, 3]).latest('created_on')
        except ManualBooking.DoesNotExist:
            booking = None
        data = {
            'commission': {
                'amount': booking.commission if booking else 0,
                'editable': True if booking else True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            },
        }
    elif source_office_id == 3:
        data = {
            'commission': {
                'amount': 0,
                'editable': True
            },
            'lr_cost': {
                'amount': 200,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 200,
                'editable': True
            },
        }
    elif source_office_id == 1:
        if freight_to_owner < 10000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 100,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        elif 10000 <= freight_to_owner < 30000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 200,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        elif 30000 <= freight_to_owner < 70000:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 300,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                },
            }
        else:
            data = {
                'commission': {
                    'amount': 0,
                    'editable': True
                },
                'lr_cost': {
                    'amount': 0,
                    'editable': True
                },
                'deduction_for_advance': {
                    'amount': 400,
                    'editable': True
                },
                'deduction_for_balance': {
                    'amount': 0,
                    'editable': True
                }
            }
    else:
        data = {
            'commission': {
                'amount': 0,
                'editable': True
            },
            'lr_cost': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_advance': {
                'amount': 0,
                'editable': True
            },
            'deduction_for_balance': {
                'amount': 0,
                'editable': True
            }
        }
    return data
