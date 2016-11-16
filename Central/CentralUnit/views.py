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
    latest_temps = Temperature.objects.order_by('-reading_time')[:5]
    current_temperature = [t.sensor_value for t in latest_temps][0]
    history_temperature = list()
    for t in latest_temps:
        history_temperature.append(t.sensor_value)

    temperature_motor = 'up'
    if [t.screen_position for t in latest_temps][0] == 1:
        temperature_motor = 'down'

    latest_lights = Light.objects.order_by('-reading_time')[:5]
    current_light = [l.sensor_value for l in latest_lights][0]
    history_lights = list()
    for l in latest_lights:
        history_lights.append(l.sensor_value)

    light_motor = 'up'
    if [l.screen_position for l in latest_lights][0] == 1:
        light_motor = 'down'

    return JsonResponse({
        'light': current_light,
        'light_motor': light_motor,
        'history_lights': history_temperature,
        'temperature': current_temperature,
        'temperature_motor': temperature_motor,
        'history_temperature': history_temperature
    })
