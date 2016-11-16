from django.http import JsonResponse
from django.shortcuts import render
from .models import Temperature, Light


def index(request):
    context = dict()

    latest_temp = Temperature.objects.order_by('-reading_time')[:1]
    latest_light = Light.objects.order_by('-reading_time')[:1]
    context['temperature'] = [t.sensor_value for t in latest_temp][0]
    context['light'] = [l.sensor_value for l in latest_light][0]
    return render(request, 'CentralUnit/index.html', context)


def sensors(request):
    latest_temp = Temperature.objects.order_by('-reading_time')[:1]
    current_temperature = [t.sensor_value for t in latest_temp][0]
    latest_light = Light.objects.order_by('-reading_time')[:1]
    current_light = [l.sensor_value for l in latest_light][0]
    return JsonResponse({
        'light': current_light,
        'temperature' : current_temperature
    })
