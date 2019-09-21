from django.conf.urls import url
from supplier import views

supplier_urlpatterns = [
    url(r'^supplier-register-page/$', views.SupplierPageView.as_view({'get': 'create'})),
    url(r'^driver-register-page/$', views.DriverPageView.as_view({'get': 'create'})),
    url(r'^vehicle-register-page/$', views.VehiclePageView.as_view({'get': 'create'})),
]
