from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MoodSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_input_text', models.TextField()),
                ('detected_mood', models.CharField(
                    choices=[('sad','Sad'),('anxious','Anxious'),('angry','Angry'),('happy','Happy'),('tired','Tired'),('confused','Confused'),('calm','Calm'),('lonely','Lonely')],
                    db_index=True, max_length=20,
                )),
                ('mood_intensity', models.CharField(
                    choices=[('low','Low'),('medium','Medium'),('high','High')],
                    default='medium', max_length=10,
                )),
                ('sentiment', models.CharField(
                    choices=[('positive','Positive'),('negative','Negative'),('neutral','Neutral')],
                    default='neutral', max_length=10,
                )),
                ('polarity_score', models.FloatField(default=0.0)),
                ('vader_compound', models.FloatField(default=0.0)),
                ('ai_response', models.TextField()),
                ('llm_used', models.CharField(default='fallback', max_length=20)),
                ('input_type', models.CharField(
                    choices=[('text','Text'),('voice','Voice')],
                    default='text', max_length=10,
                )),
                ('response_time_ms', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user', models.ForeignKey(
                    db_index=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mood_sessions',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'fc_mood_sessions',
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'created_at'], name='fc_mood_ses_user_id_idx'),
                    models.Index(fields=['detected_mood'], name='fc_mood_ses_mood_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='UserMoodStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sessions', models.PositiveIntegerField(default=0)),
                ('most_frequent_mood', models.CharField(blank=True, default='', max_length=20)),
                ('mood_counts', models.JSONField(default=dict)),
                ('average_polarity', models.FloatField(default=0.0)),
                ('last_session_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='mood_stats',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'fc_user_mood_stats',
            },
        ),
        migrations.CreateModel(
            name='DailyMoodLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_date', models.DateField(db_index=True)),
                ('dominant_mood', models.CharField(max_length=20)),
                ('session_count', models.PositiveIntegerField(default=0)),
                ('avg_polarity', models.FloatField(default=0.0)),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='daily_logs',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'db_table': 'fc_daily_mood_log',
                'ordering': ['-log_date'],
                'unique_together': {('user', 'log_date')},
            },
        ),
    ]
