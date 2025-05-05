from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("accounts/", views.user_management, name="user_management"),
    path("dashboard/", views.dashboard, name="dashboard"),

    #STORAGE URLS
    path('storage/', views.storage_management, name='storage_management'),
    path('ajax/load-subclassifications/', views.load_subclassifications, name='ajax_load_subclassifications'),
    path('ajax/load-subsets/', views.load_subsets, name='ajax_load_subsets'),

    #RIS URLS
    path('ris/', views.ris_management, name='ris_management'),
    path('ajax/load-rissubclassifications/', views.load_rissubclassifications, name='ajax_load_rissubclassifications'),

    #LOT URLS
    path('lot/', views.lot_management, name='lot_management'),

    #BUILDING URLS
    path('building/', views.building_management, name='building_management'),

    #PARKING URLS
    path('parking/', views.parking_management, name='parking_management'),

    #DISTRIBUTION URLS
    path('distributions/', views.distribution_management, name='distribution_management'),

    #OPT URLS
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]