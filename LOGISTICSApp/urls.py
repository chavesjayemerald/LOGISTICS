from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("signup/", views.user_signup, name="signup"),
    path("dashboard/", views.dashboard, name="dashboard"),

    #STORAGE URLS
    path('storage/', views.storage_management, name='storage_management'),
    path('ajax/load-subclassifications/', views.load_subclassifications, name='ajax_load_subclassifications'),
    path('ajax/load-subsets/', views.load_subsets, name='ajax_load_subsets'),

    #RIS URLS
    path('ris/', views.ris_management, name='ris_management'),
    path('ajax/load-rissubclassifications/', views.load_rissubclassifications, name='ajax_load_rissubclassifications'),
]