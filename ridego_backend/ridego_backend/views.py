from django.http import JsonResponse
import json

def payment_success(request):
    if request.method == "POST":
        data = json.loads(request.body)

        ride_id = data.get("ride_id")
        payment_id = data.get("payment_id")

        print("Ride:", ride_id)
        print("Payment:", payment_id)

        return JsonResponse({"status": "success"})