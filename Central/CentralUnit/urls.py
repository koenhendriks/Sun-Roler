from django.conf.urls import url
from . import views

urlpatterns = [
    url('sensors', views.sensors, name='index'),
    url(r'^$', views.index, name='index'),
]