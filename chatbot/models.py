from django.db import models
from django.conf import settings


class MoodSession(models.Model):
    """
    Stores every user interaction in MySQL.
    Table: fc_mood_sessions
    """
    MOOD_CHOICES = [
        ('sad',      'Sad'),
        ('anxious',  'Anxious'),
        ('angry',    'Angry'),
        ('happy',    'Happy'),
        ('tired',    'Tired'),
        ('confused', 'Confused'),
        ('calm',     'Calm'),
        ('lonely',   'Lonely'),
    ]
    INTENSITY_CHOICES = [
        ('low',    'Low'),
        ('medium', 'Medium'),
        ('high',   'High'),
    ]
    INPUT_CHOICES = [
        ('text',  'Text'),
        ('voice', 'Voice'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral',  'Neutral'),
    ]

    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_sessions',
        db_index=True,
    )
    user_input_text = models.TextField()
    detected_mood   = models.CharField(max_length=20, choices=MOOD_CHOICES, db_index=True)
    mood_intensity  = models.CharField(max_length=10, choices=INTENSITY_CHOICES, default='medium')
    sentiment       = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
    polarity_score  = models.FloatField(default=0.0)
    vader_compound  = models.FloatField(default=0.0)
    ai_response     = models.TextField()
    llm_used        = models.CharField(max_length=20, default='fallback')   # groq | ollama | fallback
    input_type      = models.CharField(max_length=10, choices=INPUT_CHOICES, default='text')
    response_time_ms = models.PositiveIntegerField(default=0)               # LLM latency tracking
    created_at      = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table   = 'fc_mood_sessions'
        ordering   = ['-created_at']
        indexes    = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['detected_mood']),
        ]

    def __str__(self):
        return f'{self.user.username} | {self.detected_mood} | {self.created_at:%Y-%m-%d %H:%M}'


class UserMoodStats(models.Model):
    """
    Aggregated mood statistics per user — updated after every session.
    Table: fc_user_mood_stats
    """
    user                 = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mood_stats',
    )
    total_sessions       = models.PositiveIntegerField(default=0)
    most_frequent_mood   = models.CharField(max_length=20, blank=True, default='')
    mood_counts          = models.JSONField(default=dict)    # {'sad': 5, 'happy': 12, ...}
    average_polarity     = models.FloatField(default=0.0)
    last_session_at      = models.DateTimeField(null=True, blank=True)
    updated_at           = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fc_user_mood_stats'

    def update(self, mood: str, polarity: float):
        """Update stats after a new session"""
        from django.utils import timezone
        self.total_sessions += 1
        counts = self.mood_counts or {}
        counts[mood] = counts.get(mood, 0) + 1
        self.mood_counts = counts
        self.most_frequent_mood = max(counts, key=counts.get)
        # Running average polarity
        n = self.total_sessions
        self.average_polarity = ((self.average_polarity * (n - 1)) + polarity) / n
        self.last_session_at = timezone.now()
        self.save()

    def __str__(self):
        return f'{self.user.username} — {self.total_sessions} sessions'


class DailyMoodLog(models.Model):
    """
    Daily mood aggregation for analytics / charts.
    Table: fc_daily_mood_log
    """
    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_logs',
    )
    log_date        = models.DateField(db_index=True)
    dominant_mood   = models.CharField(max_length=20)
    session_count   = models.PositiveIntegerField(default=0)
    avg_polarity    = models.FloatField(default=0.0)

    class Meta:
        db_table   = 'fc_daily_mood_log'
        unique_together = ('user', 'log_date')
        ordering   = ['-log_date']

    def __str__(self):
        return f'{self.user.username} | {self.log_date} | {self.dominant_mood}'
