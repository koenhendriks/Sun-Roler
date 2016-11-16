from django.conf.urls import url
from . import views

urlpatterns = [
    url('temperature', views.temperature, name='index'),
    url('light', views.light, name='index'),
    url(r'^$', views.index, name='index'),
]