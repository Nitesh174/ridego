from django.urls import path
from . import views
from .views import login_page


urlpatterns = [
    path('signup/', views.signup),
    path('login/', views.login),
      path('login/', login_page),
]
