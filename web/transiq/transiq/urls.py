"""transiq URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.views.defaults import page_not_found, server_error, permission_denied, bad_request
from django.views.generic import RedirectView

from api.urls import api_blackbuck_url_patterns
from authentication.urls import authUrlPattern
from broker.urls import broker_url_pattern
from customer.urls import api_customer_url_patterns
from datacollection.urls import dataCollectionUrlPattern
from driver.urls import api_driver_url_patterns
from enquiry.urls import enquiryUrlPattern
from fms.urls import api_fms_url_patterns
from index.url import indexUrlPattern
from index.views import index, begin_password_reset, daily_freight_page, track_shipment_display, track_shipment_page, \
    login_page
from mobile.views import m_login_page
from notification.urls import notification_url_pattern
from owner.urls import owner_urls
from report.urls import report_url_patterns
from restapi.urls import mobile_view_url_pattern
from restapi.urls import restapi_urlpatterns, page_url_patterns
from sme.urls import smeUrlPattern, smeAppUrlPattern
from sme.views import customer_login_page
from supplier.urls import supplier_urlpatterns
from team.urls import teamUrlPattern
from transporter.urls import transporterUrlPattern
from utils.urls import utils_url_patterns

handler400 = bad_request
handler403 = permission_denied
handler404 = page_not_found
handler500 = server_error

admin.site.site_header = 'Trans IQ Administration'
admin.site.index_title = 'Trans IQ Administration/ Admin'
admin.site.site_title = 'Admin site admin'
favicon_view = RedirectView.as_view(url='/static/aaho/images/logo/favicon.ico', permanent=True)
apple_touch_view = RedirectView.as_view(url='/static/aaho/images/logo/apple-icon-57x57.png', permanent=True)
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^customer/', include(smeUrlPattern)),
    url(r'^authentication', include(authUrlPattern)),
    url(r'^index/', include(indexUrlPattern)),
    url(r'^broker/', include(broker_url_pattern)),
    url(r'^rates/', daily_freight_page),
    url(r'^team/', include(teamUrlPattern)),
    url(r'^utils/', include(utils_url_patterns)),
    url(r'^owner/', include(owner_urls)),
    url(r'^transporter/', include(transporterUrlPattern)),
    url(r'^enquiry/', include(enquiryUrlPattern)),
    url(r'^data-collection', include(dataCollectionUrlPattern)),
    url(r'^m/$', m_login_page),
    url(r'^customer-login/$', customer_login_page),
    # url(r'^mobile/', include(mobile_url_pattern)),
    url(r'^mobile/', include(mobile_view_url_pattern)),
    url(r'^api/driver/', include(api_driver_url_patterns)),
    url(r'^api/customer/', include(api_customer_url_patterns)),
    url(r'^api/fms/', include(api_fms_url_patterns)),
    url(r'^report/', include(report_url_patterns)),
    url(r'^supplier/', include(supplier_urlpatterns)),
    url(r'^blackbuck/', include(api_blackbuck_url_patterns)),
    url(r'^$', index),
    url(r'^login/$', login_page),
    url(r'^begin-password-reset/$', begin_password_reset),
    url(r'^track/$', track_shipment_page),
    url(r'^track-shipment/$', track_shipment_display),
    url(r'^customer-app', include(smeAppUrlPattern)),
    url(r'^notification/', include(notification_url_pattern)),
    url(r'^$', lambda x: HttpResponseRedirect('/upload/new/')),
    url(r'^api/', include(restapi_urlpatterns)),
    url(r'^page/', include(page_url_patterns)),
    url(r'^upload/', include('fileupload.urls')),
    url(r'^favicon\.ico$', favicon_view),
    url(r'^apple-touch-icon.*\.png$', favicon_view),
]
