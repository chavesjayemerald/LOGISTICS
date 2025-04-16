from django import forms
from .models import Stored

class StoredForm(forms.ModelForm):
    class Meta:
        model = Stored
        fields = '__all__'
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }
