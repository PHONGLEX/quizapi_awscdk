from django.db import models


class Psi(models.Model):
    region = models.CharField(max_length=10)
    o3_sub_index = models.FloatField(default=0)
    pm10_twenty_four_hourly = models.FloatField(default=0)
    pm10_sub_index = models.FloatField(default=0)
    co_sub_index = models.FloatField(default=0)
    pm25_twenty_four_hourly = models.FloatField(default=0)
    so2_sub_index = models.FloatField(default=0)
    updated_timestamp = models.DateTimeField()

    class Meta:
        ordering = ("-updated_timestamp",)

    def __str__(self):
        return self.region + '-' + self.updated_timestamp.strftime("%m/%d/%Y, %H:%M:%S")


class AirTemperature(models.Model):
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    temperature = models.FloatField()

    def __str__(self):
        return self.code + '-' + self.timestamp.strftime("%m/%d/%Y, %H:%M:%S")