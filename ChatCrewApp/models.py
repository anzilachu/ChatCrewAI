from django.db import models
from django.contrib.auth.models import User

class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show_name = models.CharField(max_length=100)
    character_name = models.CharField(max_length=100)
    message = models.TextField()
    character_image_url = models.URLField()  # Add this field
    timestamp = models.DateTimeField(auto_now_add=True)

class RoleplayChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    character_name = models.CharField(max_length=100)
    opponent_name = models.CharField(max_length=100)
    message = models.TextField()
    character_image_url = models.URLField(max_length=200, null=True, blank=True)
    opponent_image_url = models.URLField(max_length=200, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.character_name} vs {self.opponent_name}"
    

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    has_paid = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    last_message_date_characters = models.DateField(null=True, blank=True)
    daily_message_count_characters = models.IntegerField(default=0)
    last_message_date_roleplay = models.DateField(null=True, blank=True)
    daily_message_count_roleplay = models.IntegerField(default=0)
    last_message_date_fanchat = models.DateField(null=True, blank=True)
    daily_message_count_fanchat = models.IntegerField(default=0)

    def reset_daily_message_counts(self):
        today = timezone.now().date()
        if self.last_message_date_characters != today:
            self.daily_message_count_characters = 0
            self.last_message_date_characters = today
        if self.last_message_date_roleplay != today:
            self.daily_message_count_roleplay = 0
            self.last_message_date_roleplay = today
        if self.last_message_date_fanchat != today:
            self.daily_message_count_fanchat = 0
            self.last_message_date_fanchat = today
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class FanChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show_name = models.CharField(max_length=100)
    message = models.TextField()
    is_user_message = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')

    def __str__(self):
        return f"{self.user.username} - {self.show_name} - {self.message[:50]}"