from django.db import models

# Create your models here.


class AudioFileSerializer(models.Model):
    audio_file = models.FileField(upload_to='uploads/')
    name = models.CharField(max_length=200, default='name')
