from django import forms
from .models import Stored, Subclassification, Subset
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import User, Role, UserRole

class UserForm(forms.ModelForm):
    profile_picture = forms.FileField(required=False)
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput, label="Password", required=False
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="Confirm Password", required=False
    )

    class Meta:
        model = User
        fields = ['username', 'firstname', 'middlename', 'lastname', 'email_address', 'contact_number', 'station_id', 'rank', 'gender', 'status']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['roles'].initial = self.instance.user_roles.values_list('role', flat=True)

        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs['class'] = 'form-control'

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image and image.size > 1024 * 1024:  # 1MB
            raise ValidationError("Image file too large ( > 1MB ).")
        return image

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and password != confirm_password:
            raise ValidationError("Password and Confirm Password do not match.")
        return confirm_password

    def save(self, commit=True):
        user = super().save(commit=False)

        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data['profile_picture'].read()

        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        elif not password and self.instance.pk:
            user.password = self.instance.password  

        if commit:
            user.save()
            UserRole.objects.filter(user=user).delete()
            selected_roles = self.cleaned_data.get('roles')
            for role in selected_roles:
                UserRole.objects.create(user=user, role=role)
        return user

    def clean_email_address(self):
        email = self.cleaned_data.get('email_address')
        if email:
            qs = User.objects.filter(email_address=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("This email is already in use.")
        return email

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number and len(contact_number) < 10:
            raise forms.ValidationError("Please enter a valid contact number.")
        return contact_number

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.instance and self.instance.username == username:
            return username
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("User with this Username already exists.")
        return username


# STORAGE FORM
# forms.py
from django import forms
from .models import Stored
from .models import Subclassification, Subset

SERIAL_TYPE_CHOICES = (
    ('', '---------'),
    ('ICS', 'ICS'),
    ('PAR', 'PAR'),
)

class StoredForm(forms.ModelForm):
    new_repository_name = forms.CharField(required=False, label='New Repository Name')
    new_classification_name = forms.CharField(required=False, label='New Classification Name')
    new_subclassification_name = forms.CharField(required=False, label='New Subclassification Name')
    new_subset_name = forms.CharField(required=False, label='New Subset Name')

    # Additional fields for serial type and number
    serial_prefix = forms.ChoiceField(choices=SERIAL_TYPE_CHOICES, label='Serial Type')
    bracket_number = forms.CharField(label='Serial bracket')

    class Meta:
        model = Stored
        fields = '__all__'
        exclude = ['user']
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

    def clean(self):
        cleaned_data = super().clean()
        prefix = cleaned_data.get('serial_prefix')
        number = cleaned_data.get('bracket_number')

        if prefix and number:
            combined = f"{prefix}# {number.strip()}"
            cleaned_data['serial_type'] = combined

        return cleaned_data


# RIS FORM
from django import forms
from .models import RIS, RISSubclassification

class RISForm(forms.ModelForm):
    new_repository_name = forms.CharField(required=False, label='New Repository Name')
    new_risclassification_name = forms.CharField(required=False, label='New RIS Classification Name')
    new_rissubclassification_name = forms.CharField(required=False, label='New RIS Subclassification Name')

    class Meta:
        model = RIS
        fields = '__all__'
        exclude = ['user']
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


# LOT FORM
from django import forms
from .models import LOT, LOTClassification, Ownership, Station, Area

class LOTForm(forms.ModelForm):
    new_lotclassification_name = forms.CharField(required=False, label='New LOT Classification Name')
    new_lotarea_name = forms.CharField(required=False, label='New Area Name')


    class Meta:
        model = LOT
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(LOTForm, self).__init__(*args, **kwargs)
        self.fields['lotclass_id'].required = False
        self.fields['owner_id'].required = False
        self.fields['area_id'].required = False
        self.fields['station_id'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        

# BUILDING FORM
from django import forms
from .models import Building, BuildingClassification, Ownership, Station, Area


class BuildingForm(forms.ModelForm):
    new_buildingclassification_name = forms.CharField(required=False, label='New Building Classification Name')
    new_buildingarea_name = forms.CharField(required=False, label='New Area Name')


    class Meta:
        model = Building
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(BuildingForm, self).__init__(*args, **kwargs)
        self.fields['buildingclass_id'].required = False
        self.fields['owner_id'].required = False
        self.fields['area_id'].required = False
        self.fields['station_id'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# PARKING FORM
from django import forms
from .models import Parking, Location, Vehicle


class ParkingForm(forms.ModelForm):
    new_parkinglocation_name = forms.CharField(required=False, label='New Location Name')
    new_parkingvehicle_name = forms.CharField(required=False, label='New Vehicle Name')


    class Meta:
        model = Parking
        fields = '__all__'
        exclude = ['user']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ParkingForm, self).__init__(*args, **kwargs)
        self.fields['location_id'].required = False
        self.fields['vehicle_id'].required = False
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


# DISTRIBUTION FORM
from django import forms
from .models import Distribution, Stored, RIS, Repository

class DistributionForm(forms.ModelForm):
    repository_id = forms.ChoiceField(choices=[], required=True, label='Repository')

    class Meta:
        model = Distribution
        fields = ['store', 'ris', 'repository_id', 'distribution_memo', 'end_user',
                  'date_received', 'date_acquired', 'unit_quantity', 'amount']
        widgets = {
            'date_received': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_acquired': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'store': forms.Select(attrs={'class': 'form-control', 'id': 'store-field'}),
            'ris': forms.Select(attrs={'class': 'form-control', 'id': 'ris-field'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop user from kwargs if passed
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Repository choices
        repo_choices = [(repo.repository_id, repo.repository_name) for repo in Repository.objects.all()]
        self.fields['repository_id'].choices = repo_choices
        self.fields['repository_id'].widget.attrs.update({'class': 'form-control'})

        self.fields['store'].required = False
        self.fields['ris'].required = False

        # Only show stores/ris created by users in the same station
        if user:
            station_id = user.station_id
            self.fields['store'].queryset = Stored.objects.filter(user__station_id=station_id)
            self.fields['ris'].queryset = RIS.objects.filter(user__station_id=station_id)

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
