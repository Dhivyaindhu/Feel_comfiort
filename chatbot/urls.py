from django.urls import path
from . import views

urlpatterns = [
    path('',           views.chat_view,      name='chat'),
    path('send/',      views.process_text,   name='process_text'),
    path('voice/',     views.process_voice,  name='process_voice'),
    path('history/',   views.mood_history,   name='mood_history'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
