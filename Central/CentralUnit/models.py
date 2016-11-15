from django.db import models


# Create your models here.

class Anemometer(models.Model):
    db_table = 'anemometer'
    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()


class Humidity(models.Model):
    db_table = 'humidity'
    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()


class Light(models.Model):
    db_table = 'light'
    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()


class Rain(models.Model):
    db_table = 'rain'
    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()


class Temperature(models.Model):
    db_table = 'temperature'
    ID = models.IntegerField(primary_key=True)
    sensor_value = models.IntegerField()
    screen_position = models.IntegerField()
    reading_time = models.IntegerField()


class Log(models.Model):
    db_table = 'log'
    ID = models.IntegerField(primary_key=True)
    message = models.TextField()
    log_time = models.IntegerField()


class SensorSettings(models.Model):
    db_table = 'sensor_settings'
    ID = models.IntegerField(primary_key=True)
    sensor = models.IntegerField()
    setting_name = models.TextField()
    setting_value = models.TextField()
