from django.urls import path
from .views import IndexView, QrCodeView

app_name = 'generator'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('qrcode/', QrCodeView.as_view(), name='qrcode'),
]
