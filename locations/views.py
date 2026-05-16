from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Country, Province, District, Sector, Cell, Village


def _json(qs):
    return JsonResponse(list(qs.values('id', 'name')), safe=False)


@login_required
def countries_list(request):
    return JsonResponse(
        list(Country.objects.values('id', 'name', 'phone_code', 'iso_code')),
        safe=False
    )


@login_required
def provinces(request):
    country_id = request.GET.get('country_id', '')
    if not country_id:
        return JsonResponse([], safe=False)
    return _json(Province.objects.filter(country_id=country_id))


@login_required
def districts(request):
    province_id = request.GET.get('province_id', '')
    if not province_id:
        return JsonResponse([], safe=False)
    return _json(District.objects.filter(province_id=province_id))


@login_required
def sectors(request):
    district_id = request.GET.get('district_id', '')
    if not district_id:
        return JsonResponse([], safe=False)
    return _json(Sector.objects.filter(district_id=district_id))


@login_required
def cells(request):
    sector_id = request.GET.get('sector_id', '')
    if not sector_id:
        return JsonResponse([], safe=False)
    return _json(Cell.objects.filter(sector_id=sector_id))


@login_required
def villages(request):
    cell_id = request.GET.get('cell_id', '')
    if not cell_id:
        return JsonResponse([], safe=False)
    return _json(Village.objects.filter(cell_id=cell_id))
