from django.http import HttpResponse
from django.shortcuts import render
from .models import Temperature


def index(request):
    context = dict()
    latest_temp = Temperature.objects.order_by('-reading_time')[:1]
    context['temperature'] = [t.sensor_value for t in latest_temp][0]
    return render(request, 'CentralUnit/index.html', context)
