import datetime
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
    latest_temps = Temperature.objects.order_by('-reading_time')[:10]
    current_temperature = [t.sensor_value for t in latest_temps][0]
    history_temperature_y = list()
    history_temperature_x = list()
    for t in latest_temps:
        history_temperature_y.append(t.sensor_value)
        history_temperature_x.append(
            datetime.datetime.fromtimestamp(
                int(t.reading_time)
            ).strftime('%H:%M')
        )

    temperature_motor = 'up'
    if [t.screen_position for t in latest_temps][0] == 1:
        temperature_motor = 'down'

    latest_lights = Light.objects.order_by('-reading_time')[:10]
    current_light = [l.sensor_value for l in latest_lights][0]
    history_lights_y = list()
    history_lights_x = list()
    for l in latest_lights:
        history_lights_y.append(l.sensor_value)
        history_lights_x.append(
            datetime.datetime.fromtimestamp(
                int(l.reading_time)
            ).strftime('%H:%M')
        )

    light_motor = 'up'
    if [l.screen_position for l in latest_lights][0] == 1:
        light_motor = 'down'

    return JsonResponse({
        'light': current_light,
        'light_motor': light_motor,
        'history_lights_y': history_lights_y,
        'history_lights_x': history_lights_x,
        'temperature': current_temperature,
        'temperature_motor': temperature_motor,
        'history_temperature_y': history_temperature_y,
        'history_temperature_x': history_temperature_x
    })
