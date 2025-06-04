from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FacebookNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Add this field
    video_id = models.CharField(max_length=100, unique=True)
    last_checked = models.DateTimeField(default=timezone.now)  # Stores creation time only

    def __str__(self):
        return self.video_id
    

class VideoCategory(models.TextChoices):
    ENTERTAINMENT = 'entertainment', 'Entertainment'
    EDUCATION = 'education', 'Education'
    GAMING = 'gaming', 'Gaming'
    MUSIC = 'music', 'Music'
    NEWS = 'news', 'News'
    TECH = 'tech', 'Technology'
    OTHER = 'other', 'Other'

class LanguageInfo(models.Model):
    primary = models.CharField(max_length=10)
    subtitles = models.JSONField(default=list)

class ChannelInfo(models.Model):
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=255)
    subscribers = models.CharField(max_length=50)

class Video(models.Model):
    title = models.CharField(max_length=255)
    video_id = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    thumbnail = models.URLField()
    channel_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=100)
    subscribers = models.CharField(max_length=50)
    category = models.CharField(
        max_length=20,
        choices=VideoCategory.choices,
        default=VideoCategory.OTHER
    )
    duration = models.CharField(max_length=20)
    duration_seconds = models.IntegerField()
    views = models.CharField(max_length=50)
    likes = models.CharField(max_length=50)
    dislikes = models.CharField(max_length=50)
    upload_date = models.DateTimeField()
    languages = models.ForeignKey(LanguageInfo, on_delete=models.CASCADE, null=True, blank=True)
    channel_info = models.ForeignKey(ChannelInfo, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)