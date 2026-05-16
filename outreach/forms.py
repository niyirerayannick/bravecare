from django import forms
from .models import OutreachCampaign


class OutreachCampaignForm(forms.ModelForm):
    class Meta:
        model = OutreachCampaign
        fields = ['title', 'description', 'start_date', 'end_date',
                  'status', 'target_population', 'reached_count']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'target_population': forms.NumberInput(attrs={'class': 'form-input'}),
            'reached_count': forms.NumberInput(attrs={'class': 'form-input'}),
        }
