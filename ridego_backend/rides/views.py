from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Ride
from drivers.models import Driver
from users.models import User
from .serializers import RideSerializer

import razorpay
from django.conf import settings
import math


# ---------------- HOME ----------------
def home(request):
    return HttpResponse("RideGo Backend Running 🚖")


# ---------------- MAP PAGE ----------------
def map_view(request):
    return render(request, 'map.html')


# ---------------- DISTANCE (FIXED) ----------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


# ---------------- FARE ----------------
def calculate_fare(distance):
    base_fare = 30
    per_km = 12
    return round(base_fare + (distance * per_km), 2)


# ---------------- COMMISSION ----------------
def calculate_commission(fare):
    commission = fare * 0.20
    driver_earning = fare - commission
    return round(commission, 2), round(driver_earning, 2)


# ---------------- NEAREST DRIVER ----------------
def find_nearest_driver(user_lat, user_lon):
    drivers = Driver.objects.filter(is_available=True)

    nearest_driver = None
    min_distance = float('inf')

    for driver in drivers:
        if driver.latitude is None or driver.longitude is None:
            continue

        distance = calculate_distance(
            user_lat, user_lon,
            driver.latitude, driver.longitude
        )

        if distance < min_distance:
            min_distance = distance
            nearest_driver = driver

    return nearest_driver


# ---------------- BOOK RIDE ----------------
@api_view(['POST'])
def book_ride(request):

    user_id = request.data.get('user')

    pickup_lat = request.data.get("pickup_lat")
    pickup_lon = request.data.get("pickup_lon")
    drop_lat = request.data.get("drop_lat")
    drop_lon = request.data.get("drop_lon")

    if not user_id:
        return Response({"error": "user required"}, status=400)

    if not pickup_lat or not pickup_lon or not drop_lat or not drop_lon:
        return Response({"error": "All coordinates required"}, status=400)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    pickup_lat = float(pickup_lat)
    pickup_lon = float(pickup_lon)
    drop_lat = float(drop_lat)
    drop_lon = float(drop_lon)

    driver = find_nearest_driver(pickup_lat, pickup_lon)

    if not driver:
        return Response({"message": "No drivers available"})

    # distance + fare
    distance = calculate_distance(pickup_lat, pickup_lon, drop_lat, drop_lon)
    fare = calculate_fare(distance)
    commission, driver_earning = calculate_commission(fare)

    driver.is_available = False
    driver.save()

    ride = Ride.objects.create(
        user=user,
        driver=driver,
        pickup_lat=pickup_lat,
        pickup_lng=pickup_lon,
        drop_lat=drop_lat,
        drop_lng=drop_lon,
        distance=distance,
        fare=fare,
        commission=commission,
        driver_earning=driver_earning,
        status="booked"
    )

    return Response({
        "ride": RideSerializer(ride).data,
        "distance_km": round(distance, 2),
        "fare": fare,
        "commission": commission,
        "driver_earning": driver_earning
    })


# ---------------- ACCEPT ----------------
@api_view(['POST'])
def accept_ride(request):
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"})

    ride.status = "accepted"
    ride.save()

    return Response(RideSerializer(ride).data)


# ---------------- START ----------------
@api_view(['POST'])
def start_ride(request):
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"})

    ride.status = "started"
    ride.save()

    return Response(RideSerializer(ride).data)


# ---------------- COMPLETE ----------------
@api_view(['POST'])
def complete_ride(request):
    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"})

    distance = calculate_distance(
        ride.pickup_lat,
        ride.pickup_lng,
        ride.drop_lat,
        ride.drop_lng
    )

    fare = calculate_fare(distance)
    commission, driver_earning = calculate_commission(fare)

    ride.distance = distance
    ride.fare = fare
    ride.status = "completed"

    ride.driver.is_available = True
    ride.driver.save()

    ride.save()

    return Response({
        "message": "Ride completed",
        "fare": fare,
        "commission": commission,
        "driver_earning": driver_earning
    })


# ---------------- PAYMENT (RAZORPAY READY) ----------------
@api_view(['POST'])
def create_payment(request, ride_id):
    try:
        ride = Ride.objects.get(id=ride_id)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        order = client.order.create({
            "amount": int(ride.fare * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        ride.payment_id = order['id']
        ride.save()

        return Response({
            "order_id": order['id'],
            "amount": order['amount'],
            "key": settings.RAZORPAY_KEY_ID
        })

    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"}, status=404)
    
# ---------------- CANCEL RIDE ----------------
@api_view(['POST'])
def cancel_ride(request):

    ride_id = request.data.get('ride_id')

    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"})

    if ride.status in ["completed", "cancelled"]:
        return Response({"error": "Ride already finished"})

    ride.status = "cancelled"

    if ride.driver:
        ride.driver.is_available = True
        ride.driver.save()

    ride.save()

    return Response({"message": "Ride cancelled successfully"})  

# ---------------- TRACK RIDE ----------------
@api_view(['GET'])
def track_ride(request, ride_id):

    try:
        ride = Ride.objects.get(id=ride_id)
    except Ride.DoesNotExist:
        return Response({"error": "Ride not found"})

    if not ride.driver:
        return Response({"error": "Driver not assigned"})

    driver = ride.driver

    return Response({
        "ride_id": ride.id,
        "driver_id": driver.id,
        "driver_name": driver.name,
        "latitude": driver.latitude,
        "longitude": driver.longitude,
        "status": ride.status
    })  
# ---------------- USER HISTORY ----------------
@api_view(['GET'])
def user_ride_history(request, user_id):
    rides = Ride.objects.filter(user_id=user_id)
    return Response(RideSerializer(rides, many=True).data)


# ---------------- DRIVER HISTORY ----------------
@api_view(['GET'])
def driver_ride_history(request, driver_id):
    rides = Ride.objects.filter(driver_id=driver_id)
    return Response(RideSerializer(rides, many=True).data)
     
def payment_page(request, ride_id):
    ride = Ride.objects.get(id=ride_id)
    return render(request, "payment.html", {
        "ride_id": ride.id,
        "amount": ride.fare
    })     