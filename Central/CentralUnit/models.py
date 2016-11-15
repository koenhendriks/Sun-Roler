from django.db import models


# Create your models here.

class Anemometer(models.Model):
    class Meta:
        db_table = 'anemometer'

    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()

    def __str__(self):
        return str(self.sensor_value)+'℃ at '+str(self.reading_time)


class Humidity(models.Model):
    class Meta:
        db_table = 'humidity'

    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()

    def __str__(self):
        return str(self.sensor_value)+' at '+str(self.reading_time)


class Light(models.Model):
    class Meta:
        db_table = 'light'

    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()

    def __str__(self):
        return str(self.sensor_value)+'lx at '+str(self.reading_time)


class Rain(models.Model):
    class Meta:
        db_table = 'rain'

    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()

    def __str__(self):
        return str(self.sensor_value)+' at '+str(self.reading_time)


class Temperature(models.Model):
    class Meta:
        db_table = 'temperature'

    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()

    def __str__(self):
        return str(self.sensor_value)+' at '+str(self.reading_time)


class Log(models.Model):
    class Meta:
        db_table = 'log'

    ID = models.IntegerField(primary_key=True)
    message = models.TextField()
    log_time = models.IntegerField()

    def __str__(self):
        return self.message


class SensorSettings(models.Model):
    class Meta:
        db_table = 'sensor_settings'

    ID = models.IntegerField(primary_key=True)
    sensor = models.IntegerField()
    setting_name = models.TextField()
    setting_value = models.TextField()

    def __str__(self):
        return self.setting_name+' : '+self.setting_value
