from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Driver
from .serializers import DriverSerializer
import math


# ---------------- DISTANCE (HAVERSINE - ACCURATE) ----------------
def calculate_distance(lat1, lon1, lat2, lon2):

    R = 6371  # Earth radius in KM

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


# ---------------- REGISTER DRIVER ----------------
@api_view(['POST'])
def register_driver(request):

    serializer = DriverSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Driver registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------- DRIVER LIST ----------------
@api_view(['GET'])
def driver_list(request):

    drivers = Driver.objects.all()
    serializer = DriverSerializer(drivers, many=True)

    return Response(serializer.data)


# ---------------- UPDATE DRIVER LOCATION ----------------
@api_view(['POST'])
def update_driver_location(request):

    driver_id = request.data.get('driver_id')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if not driver_id or not latitude or not longitude:
        return Response(
            {"error": "driver_id, latitude and longitude required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        driver = Driver.objects.get(id=driver_id)

        driver.latitude = float(latitude)
        driver.longitude = float(longitude)
        driver.save()

        return Response({
            "message": "Location updated successfully",
            "driver_id": driver.id,
            "latitude": driver.latitude,
            "longitude": driver.longitude
        })

    except Driver.DoesNotExist:
        return Response(
            {"error": "Driver not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# ---------------- GET DRIVER LOCATION ----------------
@api_view(['GET'])
def driver_location(request, driver_id):

    try:
        driver = Driver.objects.get(id=driver_id)

        return Response({
            "driver_id": driver.id,
            "latitude": driver.latitude,
            "longitude": driver.longitude,
            "is_available": driver.is_available
        })

    except Driver.DoesNotExist:
        return Response(
            {"error": "Driver not found"},
            status=status.HTTP_404_NOT_FOUND
        )


# ---------------- FIND NEAREST DRIVER ----------------
@api_view(['POST'])
def find_nearest_driver(request):

    pickup_lat = request.data.get('latitude')
    pickup_lon = request.data.get('longitude')

    if not pickup_lat or not pickup_lon:
        return Response(
            {"error": "latitude and longitude required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    pickup_lat = float(pickup_lat)
    pickup_lon = float(pickup_lon)

    drivers = Driver.objects.filter(is_available=True)

    nearest_driver = None
    min_distance = float('inf')

    for driver in drivers:

        if driver.latitude is None or driver.longitude is None:
            continue

        distance = calculate_distance(
            pickup_lat,
            pickup_lon,
            driver.latitude,
            driver.longitude
        )

        if distance < min_distance:
            min_distance = distance
            nearest_driver = driver

    if nearest_driver:

        return Response({
            "driver_id": nearest_driver.id,
            "driver_name": nearest_driver.name,
            "latitude": nearest_driver.latitude,
            "longitude": nearest_driver.longitude,
            "distance_km": round(min_distance, 2)
        })

    return Response({"message": "No drivers available"})


# ---------------- DRIVER TOGGLE AVAILABILITY ----------------
@api_view(['POST'])
def toggle_availability(request):

    driver_id = request.data.get('driver_id')

    try:
        driver = Driver.objects.get(id=driver_id)

        driver.is_available = not driver.is_available
        driver.save()

        return Response({
            "driver_id": driver.id,
            "is_available": driver.is_available
        })

    except Driver.DoesNotExist:
        return Response(
            {"error": "Driver not found"},
            status=status.HTTP_404_NOT_FOUND
        )