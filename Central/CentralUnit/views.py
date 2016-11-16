from django.http import JsonResponse
from django.shortcuts import render
from .models import Temperature, Light


def index(request):
    context = dict()
    latest_temp = Temperature.objects.order_by('-reading_time')[:1]
    context['temperature'] = [t.sensor_value for t in latest_temp][0]
    return render(request, 'CentralUnit/index.html', context)


def temperature(request):
    latest_temp = Temperature.objects.order_by('-reading_time')[:1]
    current_temperature = [t.sensor_value for t in latest_temp][0]
    return JsonResponse({'temperature': current_temperature})


def light(request):
    latest_light = Light.objects.order_by('-reading_time')[:1]
    current_light = [t.sensor_value for t in latest_light][0]
    return JsonResponse({'light': current_light})
