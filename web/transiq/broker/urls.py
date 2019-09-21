from django.conf.urls import url
from broker.views import broker_data

broker_url_pattern = [
    # views_receipts
    url(r'^broker-data/$', broker_data),

]
