from django.urls import path
from . import views

urlpatterns = [
    path('register-driver/', views.register_driver),
    path('drivers/', views.driver_list),
    path('update-location/', views.update_driver_location),
    path('find-driver/', views.find_nearest_driver),

    # 🔥 NEW (LIVE TRACKING)
    path('driver-location/<int:driver_id>/', views.driver_location),
]