from django.contrib import admin

from .models import Anemometer, Humidity, Light, Rain, Temperature, Log, SensorSettings

admin.site.register(Anemometer)
admin.site.register(Humidity)
admin.site.register(Light)
admin.site.register(Rain)
admin.site.register(Temperature)
admin.site.register(Log)
admin.site.register(SensorSettings)
# Register your models here.
