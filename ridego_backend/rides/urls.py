from django.urls import path
from .views import (
    home,
    map_view,
    book_ride,
    accept_ride,
    payment_page,
    start_ride,
    complete_ride,
    cancel_ride,
    track_ride,
    user_ride_history,
    driver_ride_history,
    create_payment,
    payment_page
)

urlpatterns = [
    path('', home),
    path('map/', map_view),

    # 🚖 Ride APIs
    path('book-ride/', book_ride),
    path('accept-ride/', accept_ride),
    path('start-ride/', start_ride),
    path('complete-ride/', complete_ride),
    path('cancel-ride/', cancel_ride),

    # 📍 Tracking
    path('track-ride/<int:ride_id>/', track_ride),
    path('payment/<int:ride_id>/', payment_page),

    # 📜 History
    path('user-history/<int:user_id>/', user_ride_history),
    path('driver-history/<int:driver_id>/', driver_ride_history),

    # 💳 Payment
    path('create-payment/<int:ride_id>/', create_payment),
]