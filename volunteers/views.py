from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Volunteer
from .forms import VolunteerForm
from patients.views import _apply_location, _location_json


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _form_errors(form):
    return {k: [str(e) for e in v] for k, v in form.errors.items()}


@login_required
def volunteer_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    volunteers = Volunteer.objects.all()

    if query:
        volunteers = volunteers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(role__icontains=query)
        )
    if status_filter:
        volunteers = volunteers.filter(status=status_filter)

    context = {
        'volunteers': volunteers,
        'query': query,
        'status_filter': status_filter,
        'active_count': Volunteer.objects.filter(status='active').count(),
        'inactive_count': Volunteer.objects.filter(status='inactive').count(),
        'total_count': Volunteer.objects.count(),
    }
    return render(request, 'volunteers/list.html', context)


@login_required
def volunteer_add(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            vol = form.save(commit=False)
            _apply_location(vol, request.POST)
            vol.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': f'{vol.get_full_name()} added as volunteer.'})
            messages.success(request, f'Volunteer {vol.get_full_name()} added.')
            return redirect('volunteers:list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    form = VolunteerForm()
    return render(request, 'volunteers/form.html', {'form': form, 'title': 'Add Volunteer'})


@login_required
def volunteer_edit(request, pk):
    vol = get_object_or_404(Volunteer, pk=pk)
    if request.method == 'POST':
        form = VolunteerForm(request.POST, instance=vol)
        if form.is_valid():
            vol = form.save(commit=False)
            _apply_location(vol, request.POST)
            vol.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Volunteer updated.'})
            messages.success(request, 'Volunteer updated.')
            return redirect('volunteers:list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    form = VolunteerForm(instance=vol)
    return render(request, 'volunteers/form.html', {'form': form, 'title': 'Edit Volunteer', 'volunteer': vol})


@login_required
def volunteer_json(request, pk):
    v = get_object_or_404(Volunteer, pk=pk)
    data = {
        'first_name': v.first_name,
        'last_name': v.last_name,
        'phone': v.phone,
        'email': v.email,
        'role': v.role,
        'status': v.status,
    }
    data.update(_location_json(v))
    return JsonResponse(data)
