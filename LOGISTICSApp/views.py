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


@guest_required
def home(request):
    return render(request, 'home.html')


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
            email_address=email_address,
            contact_number=contact_number
        )

        messages.success(request, "Account created successfully! You can now log in.")
        return redirect("login")

    return render(request, "authentication/signup.html")


# DASHBOARD
@login_required
def dashboard(request):
    
    return render(request, "dashboard.html")


# STORAGE MANAGEMENT
from django.shortcuts import render, get_object_or_404, redirect
from .models import Stored, Repository, Classification
from .forms import StoredForm

def storage_management(request):
    stored_list = Stored.objects.all()
    form = StoredForm()

    if request.method == 'POST':
        form = StoredForm(request.POST)
        if form.is_valid():
            # Repository
            repository = form.cleaned_data.get('repository_id')
            if not repository:
                new_repo_name = form.cleaned_data.get('new_repository_name')
                if new_repo_name:
                    repository, _ = Repository.objects.get_or_create(repository_name=new_repo_name)
                else:
                    repository = None

            # Classification
            classification = form.cleaned_data.get('class_id')
            if not classification:
                new_class_name = form.cleaned_data.get('new_classification_name')
                if new_class_name:
                    classification, _ = Classification.objects.get_or_create(class_name=new_class_name)
                else:
                    classification = None

            # Subclassification
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

            # Subset
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

            # Save Stored
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
