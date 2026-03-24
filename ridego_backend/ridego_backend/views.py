from django.http import JsonResponse
from django.conf import settings
import razorpay
import json

def payment_success(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            payment_id = data.get("razorpay_payment_id")
            order_id = data.get("razorpay_order_id")
            signature = data.get("razorpay_signature")

            client = razorpay.Client(auth=(
                settings.RAZORPAY_KEY_ID,
                settings.RAZORPAY_KEY_SECRET
            ))

            # 🔐 Verify signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # ✅ OPTIONAL (future use)
            # yaha tum ride status update kar sakte ho
            # Ride.objects.filter(id=ride_id).update(status="completed")

            return JsonResponse({
                "status": "Payment Verified ✅"
            })

        except Exception as e:
            print("Payment Error:", str(e))

            return JsonResponse({
                "status": "Payment Failed ❌"
            })

    return JsonResponse({
        "error": "Invalid request"
    })