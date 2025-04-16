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