from django.conf.urls import url
from api import views

api_blackbuck_url_patterns = [
    # get
    url(r'list/$', views.blackbuck_list),
    url(r'file/(?P<filename>.+)/$', views.blackbuck_file),
]
