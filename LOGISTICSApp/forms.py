from django import forms
from .models import Stored, Subclassification, Subset

class StoredForm(forms.ModelForm):
    class Meta:
        model = Stored
        fields = '__all__'
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(StoredForm, self).__init__(*args, **kwargs)
        self.fields['subclass_id'].queryset = Subclassification.objects.none()
        self.fields['subset_id'].queryset = Subset.objects.none()

        if 'class_id' in self.data:
            try:
                class_id = int(self.data.get('class_id'))
                self.fields['subclass_id'].queryset = Subclassification.objects.filter(class_id=class_id)
            except (ValueError, TypeError):
                pass

        if 'subclass_id' in self.data:
            try:
                subclass_id = int(self.data.get('subclass_id'))
                self.fields['subset_id'].queryset = Subset.objects.filter(subclass_id=subclass_id)
            except (ValueError, TypeError):
                pass
