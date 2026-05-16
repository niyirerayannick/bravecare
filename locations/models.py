from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    phone_code = models.CharField(max_length=10)
    iso_code = models.CharField(max_length=3, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'countries'

    def __str__(self):
        return f"{self.name} ({self.phone_code})"


class Province(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='provinces')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name='districts')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Sector(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sectors')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Cell(models.Model):
    name = models.CharField(max_length=100)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='cells')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Village(models.Model):
    name = models.CharField(max_length=100)
    cell = models.ForeignKey(Cell, on_delete=models.CASCADE, related_name='villages')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
