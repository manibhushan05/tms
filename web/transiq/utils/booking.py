from team.models import ManualBooking
import pandas as pd
from datetime import date, datetime


def get_lr_data():
    mb = ManualBooking.objects.values_list('id', 'booking_id', 'consignor_name', 'consignor_address', 'consignor_city',
                                           'consignor_city_fk', 'consignor_pin', 'consignor_phone', 'consignor_cst_tin',
                                           'consignee_name', 'consignee_address', 'consignee_city', 'consignee_city_fk',
                                           'consignee_pin', 'consignee_phone', 'consignee_cst_tin', 'unloading_date',
                                           'from_city',
                                           'to_city', 'road_permit_number', 'party_invoice_number',
                                           'party_invoice_date',
                                           'party_invoice_amount', 'is_insured', 'insurance_provider',
                                           'insurance_policy_number',
                                           'insured_amount', 'insurance_date', 'insurance_risk',
                                           'liability_of_service_tax')
    df = pd.DataFrame(data=list(mb),
                      columns=['id', 'booking_id', 'consignor_name', 'consignor_address', 'consignor_city',
                               'consignor_city_fk', 'consignor_pin', 'consignor_phone', 'consignor_cst_tin',
                               'consignee_name', 'consignee_address', 'consignee_city', 'consignee_city_fk',
                               'consignee_pin', 'consignee_phone', 'consignee_cst_tin', 'unloading_date',
                               'from_city',
                               'to_city', 'road_permit_number', 'party_invoice_number', 'party_invoice_date',
                               'party_invoice_amount', 'is_insured', 'insurance_provider',
                               'insurance_policy_number',
                               'insured_amount', 'insurance_date', 'insurance_risk', 'liability_of_service_tax'])
    df.to_excel('/home/mani/Desktop/booking_lr_' + datetime.today().strftime('%Y%m%d%H%M') + '.xlsx', index=False)
