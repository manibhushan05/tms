from sme.models import Sme
from datetime import datetime
import pandas as pd


def customers_data():
    data = []
    for customer in Sme.objects.order_by('-created_on'):
        data.append([
            customer.id,
            customer.get_name(),
            customer.company_code,
            customer.city.name if customer.city else '',
            customer.aaho_poc.emp_name() if customer.aaho_poc else '',
            customer.gstin,
            customer.get_is_gst_applicable_display(),
        ])
    df = pd.DataFrame(data=data, columns=['ID', 'Name', 'Code', 'City', 'POC', 'GSTIN', 'GSTIN Applicable'])
    df.to_excel('customers_data {}.xlsx'.format(datetime.now().strftime('%d-%b-%Y %I:%M:%S %p')), index=False)