from django.conf.urls import url
from utils import views

utils_url_patterns = [
    url(r'^cities-data/$', view=views.city_data),
    # url(r'^states-data/$', view=views.state_data),
    # url(r'^customers-data/$', view=views.customers_data),
    # url(r'^employees-data/$', view=views.employees_data),
    # url(r'^vehicles-data/$', view=views.vehicles_data),
    # url(r'^suppliers-data/$', view=views.brokers_data),
    # url(r'^drivers-data/$', view=views.drivers_data),
    # url(r'^owners-data/$', view=views.owners_data),
    # url(r'^invoice-number-data/$', view=views.invoice_number_data),
    # url(r'^booking_id-lr_number-data/$', view=views.booking_id_lr_data),
    # url(r'^vehicle-categories-data/$', view=views.vehicle_categories_data),
    # url(r'^aaho-office-data/$', view=views.aaho_office_data)
]
