from django.contrib import admin
from .models import Country, Province, District, Sector, Cell, Village


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_code', 'iso_code']
    search_fields = ['name', 'iso_code']


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['country']
    search_fields = ['name']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'province']
    list_filter = ['province__country', 'province']
    search_fields = ['name']


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ['name', 'district']
    list_filter = ['district__province', 'district']
    search_fields = ['name']


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ['name', 'sector']
    list_filter = ['sector__district']
    search_fields = ['name']


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['name', 'cell']
    list_filter = ['cell__sector__district']
    search_fields = ['name']
