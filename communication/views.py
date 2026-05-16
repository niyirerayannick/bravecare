from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import CommunicationMessage
from .forms import CommunicationMessageForm


def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _form_errors(form):
    return {field: [str(e) for e in errors] for field, errors in form.errors.items()}


@login_required
def communication_center(request):
    status_filter = request.GET.get('status', '')
    qs = CommunicationMessage.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)

    context = {
        'recent_messages': qs[:50],
        'status_filter': status_filter,
        'sent_count': CommunicationMessage.objects.filter(status='sent').count(),
        'delivered_count': CommunicationMessage.objects.filter(status='delivered').count(),
        'draft_count': CommunicationMessage.objects.filter(status='draft').count(),
    }
    return render(request, 'communication/center.html', context)


@login_required
def message_add(request):
    if request.method == 'POST':
        form = CommunicationMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sent_by = request.user
            msg.status = 'sent'
            msg.sent_at = timezone.now()
            msg.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Message sent successfully.'})
            messages.success(request, 'Message sent successfully.')
            return redirect('communication:center')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('communication:center')


@login_required
def message_edit(request, pk):
    msg_obj = get_object_or_404(CommunicationMessage, pk=pk)
    if request.method == 'POST':
        form = CommunicationMessageForm(request.POST, instance=msg_obj)
        if form.is_valid():
            form.save()
            if _is_ajax(request):
                return JsonResponse({'success': True, 'message': 'Message updated successfully.'})
            messages.success(request, 'Message updated.')
            return redirect('communication:center')
        if _is_ajax(request):
            return JsonResponse({'success': False, 'errors': _form_errors(form)}, status=400)
    return redirect('communication:center')


@login_required
def message_json(request, pk):
    msg_obj = get_object_or_404(CommunicationMessage, pk=pk)
    return JsonResponse({
        'recipient': msg_obj.recipient,
        'message_type': msg_obj.message_type,
        'subject': msg_obj.subject,
        'message': msg_obj.message,
    })
