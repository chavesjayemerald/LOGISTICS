from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
from functools import wraps
from .models import UserRole

def guest_required(view_func):
    """
    Decorator to restrict access to only unauthenticated users.
    Redirects authenticated users to the dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You need to be logged in to access this page.")

            try:
                has_role = UserRole.objects.filter(user=request.user, role__role_name=required_role).exists()

                if not has_role:
                    return render(request, 'access_denied.html', {'role_error': True})

            except Exception as e:
                print(f"[Role Check Error] {e}")
                return HttpResponseForbidden("Permission check failed.")

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator