from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended User model — stored in MySQL feel_comfort_db.users_customuser
    All fields below are additional to Django's default username/email/password
    """
    phone_number    = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth   = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    MOOD_PREF_CHOICES = [
        ('calm',      'Calm & Relaxing'),
        ('energetic', 'Energetic Activities'),
        ('mindful',   'Mindfulness & Meditation'),
        ('social',    'Social Connection'),
    ]
    mood_preference = models.CharField(
        max_length=20, choices=MOOD_PREF_CHOICES, default='calm'
    )
    total_sessions  = models.PositiveIntegerField(default=0)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fc_users'          # MySQL table name

    def __str__(self):
        return f'{self.username} ({self.email})'

    @property
    def display_name(self):
        return self.get_full_name() or self.username
