from functools import wraps
from django.shortcuts import redirect

def guest_required(view_func):
    """
    Decorator to restrict access to only unauthenticated users.
    Redirects authenticated users to the dashboard.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # Change 'dashboard' to your actual homepage or dashboard URL name
        return view_func(request, *args, **kwargs)
    return _wrapped_view
