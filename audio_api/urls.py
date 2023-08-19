from django.urls import path
from .views import AudioFileView, BuyView

urlpatterns = [
    path('audio/', AudioFileView.as_view(), name='audio-file'),
    path('buy/<str:tg_id>/<int:amount>/', BuyView.as_view(), name='buy'),
]
