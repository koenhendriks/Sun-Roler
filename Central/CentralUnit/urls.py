from django.conf.urls import url
from . import views

urlpatterns = [
    url('sensors', views.sensors, name='index'),
    url('update/rollout/(?P<value>[0-9]+)', views.updateRollOut, name='rollout'),
    url('update/rollin/(?P<value>[0-9]+)', views.updateRollIn, name='rollin'),
    url(r'^$', views.index, name='index'),
]