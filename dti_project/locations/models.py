from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Province(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='provinces')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class CityMunicipality(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class Barangay(models.Model):
    city = models.ForeignKey(CityMunicipality, on_delete=models.CASCADE, related_name='barangays')
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
