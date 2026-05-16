from django import forms
from .models import CommunicationMessage


class CommunicationMessageForm(forms.ModelForm):
    class Meta:
        model = CommunicationMessage
        fields = ['recipient', 'message_type', 'subject', 'message']
        widgets = {
            'recipient': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone number or group name'}),
            'message_type': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Message subject'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 5, 'placeholder': 'Type your message here...'}),
        }
