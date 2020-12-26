from django.urls import path
from .views import send_sms, check_sms

urlpatterns = [
    path('sending/', send_sms),
    path('checking/', check_sms)
]
