from django.urls import path
from audio_pro.views import process_audio

urlpatterns = [
    path('process-audio/', process_audio, name='process_audio'),
]
