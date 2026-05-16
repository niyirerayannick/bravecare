from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import OutreachCampaign
from .forms import OutreachCampaignForm
from patients.views import _apply_location, _location_json


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _form_errors(form):
    return {k: [str(e) for e in v] for k, v in form.errors.items()}


@login_required
def campaign_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    campaigns = OutreachCampaign.objects.all()

    if query:
        campaigns = campaigns.filter(Q(title__icontains=query) | Q(location__icontains=query))
    if status_filter:
        campaigns = campaigns.filter(status=status_filter)

    per_page = int(request.GET.get('per_page', 10))
    if per_page not in [10, 25, 50, 100]:
        per_page = 10
    paginator = Paginator(campaigns, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

    context = {
        'campaigns':  page_obj,
        'page_obj':   page_obj,
        'per_page':   per_page,
        'page_range': page_range,
        'query': query,
        'status_filter': status_filter,
        'active_count': OutreachCampaign.objects.filter(status='active').count(),
        'planned_count': OutreachCampaign.objects.filter(status='planned').count(),
        'completed_count': OutreachCampaign.objects.filter(status='completed').count(),
    }
    return render(request, 'outreach/list.html', context)


@login_required
def campaign_add(request):
    if request.method == 'POST':
        form = OutreachCampaignForm(request.POST)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.created_by = request.user
            _apply_location(campaign, request.POST)
            campaign.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': f'Campaign "{campaign.title}" created.'})
            messages.success(request, f'Campaign "{campaign.title}" created.')
            return redirect('outreach:list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    form = OutreachCampaignForm()
    return render(request, 'outreach/form.html', {'form': form, 'title': 'New Campaign'})


@login_required
def campaign_edit(request, pk):
    campaign = get_object_or_404(OutreachCampaign, pk=pk)
    if request.method == 'POST':
        form = OutreachCampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            campaign = form.save(commit=False)
            _apply_location(campaign, request.POST)
            campaign.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Campaign updated.'})
            messages.success(request, 'Campaign updated.')
            return redirect('outreach:list')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    form = OutreachCampaignForm(instance=campaign)
    return render(request, 'outreach/form.html', {'form': form, 'title': 'Edit Campaign', 'campaign': campaign})


@login_required
def campaign_json(request, pk):
    c = get_object_or_404(OutreachCampaign, pk=pk)
    data = {
        'title': c.title,
        'description': c.description,
        'start_date': str(c.start_date),
        'end_date': str(c.end_date),
        'status': c.status,
        'target_population': c.target_population,
        'reached_count': c.reached_count,
    }
    data.update(_location_json(c))
    return JsonResponse(data)


@login_required
def campaign_detail(request, pk):
    campaign = get_object_or_404(OutreachCampaign, pk=pk)
    return render(request, 'outreach/detail.html', {'campaign': campaign})
