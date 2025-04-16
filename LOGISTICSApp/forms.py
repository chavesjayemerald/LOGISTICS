from django import forms
from .models import Stored, Subclassification, Subset

class StoredForm(forms.ModelForm):
    new_repository_name = forms.CharField(required=False, label='New Repository Name')
    new_classification_name = forms.CharField(required=False, label='New Classification Name')
    new_subclassification_name = forms.CharField(required=False, label='New Subclassification Name')
    new_subset_name = forms.CharField(required=False, label='New Subset Name')

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

        self.fields['repository_id'].required = False
        self.fields['class_id'].required = False
        self.fields['subclass_id'].required = False
        self.fields['subset_id'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



from django import forms
from .models import RIS, RISSubclassification

class RISForm(forms.ModelForm):
    new_repository_name = forms.CharField(required=False, label='New Repository Name')
    new_risclassification_name = forms.CharField(required=False, label='New RIS Classification Name')
    new_rissubclassification_name = forms.CharField(required=False, label='New RIS Subclassification Name')

    class Meta:
        model = RIS
        fields = '__all__'
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }
        

    def __init__(self, *args, **kwargs):
        super(RISForm, self).__init__(*args, **kwargs)
        self.fields['rissubclass_id'].queryset = RISSubclassification.objects.none()

        if 'risclass_id' in self.data:
            try:
                risclass_id = int(self.data.get('risclass_id'))
                self.fields['rissubclass_id'].queryset = RISSubclassification.objects.filter(risclass_id=risclass_id)
            except (ValueError, TypeError):
                pass

        self.fields['repository_id'].required = False
        self.fields['risclass_id'].required = False
        self.fields['rissubclass_id'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'




