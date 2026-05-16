from django import forms
from .models import Patient, FollowUp, Screening


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'phone', 'national_id',
            'date_of_birth', 'gender', 'risk_level', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+250...', 'id': 'patientPhoneHidden'}),
            'national_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'National ID'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['patient', 'service', 'due_date', 'status', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.TextInput(attrs={'class': 'form-input'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class ScreeningForm(forms.ModelForm):
    class Meta:
        model = Screening
        fields = [
            'patient', 'screening_type', 'result', 'risk_level',
            'screening_date', 'status', 'comments', 'recommendations',
            'followup_notes', 'next_followup_date',
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'id': 'screeningPatientSelect'}),
            'screening_type': forms.Select(attrs={'class': 'form-select', 'id': 'screeningTypeSelect'}),
            'result': forms.TextInput(attrs={'class': 'form-input', 'id': 'screeningResultInput'}),
            'risk_level': forms.Select(attrs={'class': 'form-select'}),
            'screening_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3,
                                              'placeholder': 'Clinical observations and findings…'}),
            'recommendations': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3,
                                                     'placeholder': 'Treatment or action recommendations…'}),
            'followup_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2,
                                                    'placeholder': 'Notes for follow-up visit…'}),
            'next_followup_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }
