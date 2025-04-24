from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import guest_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import User


# AUTHENTICATION
@guest_required
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "authentication/login.html")


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


# PERSONNEL / INTERN CREATION
@login_required
def user_signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        firstname = request.POST.get("first_name")
        middlename = request.POST.get("middle_name")
        lastname = request.POST.get("last_name")
        rank = request.POST.get("rank")
        gender = request.POST.get("gender")
        email_address = request.POST.get("email")
        contact_number = request.POST.get("contact_number")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("signup")

        user = User.objects.create_user(
            username=username,
            password=password,
            firstname=firstname,
            gender=gender,
            middlename=middlename if middlename else None,
            lastname=lastname,
            rank=rank,
            email_address=email_address,
            contact_number=contact_number
        )

        messages.success(request, "New account created successfully!")
        return redirect("login")

    return render(request, "authentication/signup.html")


# DASHBOARD
@login_required
def dashboard(request):
    
    return render(request, "dashboard.html")


# STORAGE MANAGEMENT
from django.shortcuts import render, get_object_or_404, redirect
from .models import Stored, Repository, Classification, Subclassification, Subset
from .forms import StoredForm

@login_required
def storage_management(request):
    stored_list = Stored.objects.all()
    form = StoredForm()

    if request.method == 'POST':
        instance = None
        if 'store_id' in request.POST:
            instance = get_object_or_404(Stored, pk=request.POST['store_id'])
        
        form = StoredForm(request.POST, instance=instance)

        if form.is_valid():
            repository = form.cleaned_data.get('repository_id')
            if not repository:
                new_repo_name = form.cleaned_data.get('new_repository_name')
                if new_repo_name:
                    repository, _ = Repository.objects.get_or_create(repository_name=new_repo_name)
                else:
                    repository = None

            classification = form.cleaned_data.get('class_id')
            if not classification:
                new_class_name = form.cleaned_data.get('new_classification_name')
                if new_class_name:
                    classification, _ = Classification.objects.get_or_create(class_name=new_class_name)
                else:
                    classification = None

            subclassification = form.cleaned_data.get('subclass_id')
            if not subclassification:
                new_subclass_name = form.cleaned_data.get('new_subclassification_name')
                if new_subclass_name and classification:
                    subclassification, _ = Subclassification.objects.get_or_create(
                        subclass_name=new_subclass_name,
                        class_id=classification
                    )
                else:
                    subclassification = None

            subset = form.cleaned_data.get('subset_id')
            if not subset:
                new_subset_name = form.cleaned_data.get('new_subset_name')
                if new_subset_name and subclassification:
                    subset, _ = Subset.objects.get_or_create(
                        subset_name=new_subset_name,
                        subclass_id=subclassification
                    )
                else:
                    subset = None

            stored = form.save(commit=False)
            stored.repository_id = repository
            stored.class_id = classification
            stored.subclass_id = subclassification
            stored.subset_id = subset
            stored.save()
            return redirect('storage_management')

    elif request.GET.get('delete'):
        instance = get_object_or_404(Stored, pk=request.GET.get('delete'))
        instance.delete()
        return redirect('storage_management')

    elif request.GET.get('edit'):
        instance = get_object_or_404(Stored, pk=request.GET.get('edit'))
        form = StoredForm(instance=instance)

    attrs = {'class': 'form-control'}
    return render(request, 'storage/storage_management.html', {
        'form': form,
        'stored_list': stored_list,
        'attrs': attrs
    })




from django.http import JsonResponse
from .models import Subclassification, Subset

def load_subclassifications(request):
    class_id = request.GET.get('class_id')
    subclasses = Subclassification.objects.filter(class_id=class_id).values('subclass_id', 'subclass_name')
    return JsonResponse(list(subclasses), safe=False)

def load_subsets(request):
    subclass_id = request.GET.get('subclass_id')
    subsets = Subset.objects.filter(subclass_id=subclass_id).values('subset_id', 'subset_name')
    return JsonResponse(list(subsets), safe=False)



# RIS MANAGEMENT
from django.shortcuts import render, get_object_or_404, redirect
from .models import RIS, RISClassification, RISSubclassification
from .forms import RISForm

@login_required
def ris_management(request):
    ris_list = RIS.objects.all()
    form = RISForm()

    if request.method == 'POST':
        ris_id = request.POST.get('ris_id')
        instance = None

        if ris_id:
            instance = get_object_or_404(RIS, pk=ris_id)

        form = RISForm(request.POST, instance=instance)
        
        if form.is_valid():
            repository = form.cleaned_data.get('repository_id')
            if not repository:
                new_repo_name = form.cleaned_data.get('new_repository_name')
                if new_repo_name:
                    repository, _ = Repository.objects.get_or_create(repository_name=new_repo_name)

            risclassification = form.cleaned_data.get('risclass_id')
            if not risclassification:
                new_risclass_name = form.cleaned_data.get('new_risclassification_name')
                if new_risclass_name:
                    risclassification, _ = RISClassification.objects.get_or_create(risclass_name=new_risclass_name)

            rissubclassification = form.cleaned_data.get('rissubclass_id')
            if not rissubclassification:
                new_rissubclass_name = form.cleaned_data.get('new_rissubclassification_name')
                if new_rissubclass_name and risclassification:
                    rissubclassification, _ = RISSubclassification.objects.get_or_create(
                        rissubclass_name=new_rissubclass_name,
                        risclass_id=risclassification
                    )

            ris = form.save(commit=False)
            ris.repository_id = repository
            ris.risclass_id = risclassification
            ris.rissubclass_id = rissubclassification
            ris.ris_memo = request.POST.get('ris_memo')
            ris.save()
            return redirect('ris_management')


    elif request.GET.get('delete'):
        instance = get_object_or_404(RIS, pk=request.GET.get('delete'))
        instance.delete()
        return redirect('ris_management')

    elif request.GET.get('edit'):
        instance = get_object_or_404(RIS, pk=request.GET.get('edit'))
        form = RISForm(instance=instance)

    attrs = {'class': 'form-control'}
    return render(request, 'ris/ris_management.html', {
        'form': form,
        'ris_list': ris_list,
        'attrs': attrs
    })


from django.http import JsonResponse
from .models import RISSubclassification

def load_rissubclassifications(request):
    risclass_id = request.GET.get('risclass_id')
    rissubclasses = RISSubclassification.objects.filter(risclass_id=risclass_id).values('rissubclass_id', 'rissubclass_name')
    return JsonResponse(list(rissubclasses), safe=False)


# LOT MANAGEMENT
from .models import LOT, Ownership, Station, LOTClassification, Area
from .forms import LOTForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

@login_required
def lot_management(request):
    lot_list = LOT.objects.all()
    form = LOTForm()

    if request.method == 'POST':
        lot_id = request.POST.get('lot_id')
        instance = None

        if lot_id:
            instance = get_object_or_404(LOT, pk=lot_id)

        form = LOTForm(request.POST, instance=instance)
        
        if form.is_valid():
            owner = form.cleaned_data.get('owner_id')
            if not owner:
                new_owner_name = form.cleaned_data.get('new_lotowner_name')
                if new_owner_name:
                    owner, _ = Ownership.objects.get_or_create(owner_name=new_owner_name)

            area = form.cleaned_data.get('area_id')
            if not area:
                new_area_name = form.cleaned_data.get('new_lotarea_name')
                if new_area_name:
                    area, _ = Area.objects.get_or_create(area_name=new_area_name)

            station = form.cleaned_data.get('station_id')
            if not station:
                new_station_name = form.cleaned_data.get('new_lotstation_name')
                if new_station_name:
                    station, _ = Station.objects.get_or_create(station_name=new_station_name)

            lotclassification = form.cleaned_data.get('lotclass_id')
            if not lotclassification:
                new_lotclass_name = form.cleaned_data.get('new_lotclassification_name')
                if new_lotclass_name:
                    lotclassification, _ = LOTClassification.objects.get_or_create(lotclass_name=new_lotclass_name)

            lot = form.save(commit=False)
            lot.owner_id = owner
            lot.area_id = area
            lot.station_id = station
            lot.lotclass_id = lotclassification
            lot.lot_memo = request.POST.get('lot_memo')
            lot.save()
            return redirect('lot_management')


    elif request.GET.get('delete'):
        instance = get_object_or_404(LOT, pk=request.GET.get('delete'))
        instance.delete()
        return redirect('lot_management')

    elif request.GET.get('edit'):
        instance = get_object_or_404(LOT, pk=request.GET.get('edit'))
        form = LOTForm(instance=instance)

    attrs = {'class': 'form-control'}
    return render(request, 'lot/lot_management.html', {
        'form': form,
        'lot_list': lot_list,
        'attrs': attrs
    })


# BUILDING MANAGEMENT
from .models import Building, Ownership, Station, BuildingClassification, Area
from .forms import BuildingForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

@login_required
def building_management(request):
    building_list = Building.objects.all()
    form = BuildingForm()

    if request.method == 'POST':
        building_id = request.POST.get('building_id')
        instance = None

        if building_id:
            instance = get_object_or_404(Building, pk=building_id)

        form = BuildingForm(request.POST, instance=instance)
        
        if form.is_valid():
            owner = form.cleaned_data.get('owner_id')
            if not owner:
                new_owner_name = form.cleaned_data.get('new_buildingowner_name')
                if new_owner_name:
                    owner, _ = Ownership.objects.get_or_create(owner_name=new_owner_name)

            area = form.cleaned_data.get('area_id')
            if not area:
                new_area_name = form.cleaned_data.get('new_buildingarea_name')
                if new_area_name:
                    area, _ = Area.objects.get_or_create(area_name=new_area_name)

            station = form.cleaned_data.get('station_id')
            if not station:
                new_station_name = form.cleaned_data.get('new_buildingstation_name')
                if new_station_name:
                    station, _ = Station.objects.get_or_create(station_name=new_station_name)

            buildingclassification = form.cleaned_data.get('buildingclass_id')
            if not buildingclassification:
                new_buildingclass_name = form.cleaned_data.get('new_buildingclassification_name')
                if new_buildingclass_name:
                    buildingclassification, _ = BuildingClassification.objects.get_or_create(buildingclass_name=new_buildingclass_name)

            building = form.save(commit=False)
            building.owner_id = owner
            building.area_id = area
            building.station_id = station
            building.buildingclass_id = buildingclassification
            building.building_memo = request.POST.get('building_memo')
            building.save()
            return redirect('building_management')


    elif request.GET.get('delete'):
        instance = get_object_or_404(Building, pk=request.GET.get('delete'))
        instance.delete()
        return redirect('building_management')

    elif request.GET.get('edit'):
        instance = get_object_or_404(Building, pk=request.GET.get('edit'))
        form = BuildingForm(instance=instance)

    attrs = {'class': 'form-control'}
    return render(request, 'building/building_management.html', {
        'form': form,
        'building_list': building_list,
        'attrs': attrs
    })


# PARKING MANAGEMENT
from .models import Parking, Location, Vehicle
from .forms import ParkingForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse

@login_required
def parking_management(request):
    parking_list = Parking.objects.all()
    form = ParkingForm()

    if request.method == 'POST':
        parking_id = request.POST.get('parking_id')
        instance = None

        if parking_id:
            instance = get_object_or_404(Parking, pk=parking_id)

        form = ParkingForm(request.POST, instance=instance)
        
        if form.is_valid():
            location = form.cleaned_data.get('location_id')
            if not location:
                new_location_name = form.cleaned_data.get('new_parkinglocation_name')
                if new_location_name:
                    location, _ = Location.objects.get_or_create(location_name=new_location_name)

            vehicle = form.cleaned_data.get('vehicle_id')
            if not vehicle:
                new_vehicle_name = form.cleaned_data.get('new_parkingvehicle_name')
                if new_vehicle_name:
                    vehicle, _ = Vehicle.objects.get_or_create(vehicle_name=new_vehicle_name)

            parking = form.save(commit=False)
            parking.location_id = location
            parking.vehicle_id = vehicle
            parking.unit_quantity = request.POST.get('unit_quantity')
            parking.parking_memo = request.POST.get('parking_memo')
            parking.save()
            return redirect('parking_management')


    elif request.GET.get('delete'):
        instance = get_object_or_404(Parking, pk=request.GET.get('delete'))
        instance.delete()
        return redirect('parking_management')

    elif request.GET.get('edit'):
        instance = get_object_or_404(Parking, pk=request.GET.get('edit'))
        form = ParkingForm(instance=instance)

    attrs = {'class': 'form-control'}
    return render(request, 'parking/parking_management.html', {
        'form': form,
        'parking_list': parking_list,
        'attrs': attrs
    })