from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from django.shortcuts import render


# ---------------- SIGNUP ----------------
@api_view(['POST'])
def signup(request):

    name = request.data.get("name")
    phone = request.data.get("phone")

    user = User.objects.create(
        name=name,
        phone=phone
    )

    return Response({
        "message": "User created",
        "user_id": user.id
    })


# ---------------- LOGIN API ----------------
@api_view(['POST'])
def login(request):

    phone = request.data.get("phone")

    try:
        user = User.objects.get(phone=phone)

        return Response({
            "message": "Login successful",
            "user_id": user.id
        })

    except User.DoesNotExist:
        return Response({"error": "User not found"})


# ---------------- LOGIN PAGE ----------------
def login_page(request):
    return render(request, "login.html")