# Feel Comfort — AI Emotional Support Chatbot

A Django-based mental wellness chatbot powered by **Groq API** (free LLM) with mood detection via VADER + TextBlob NLP.

## Quick Start (5 minutes)

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (free at https://console.groq.com)
```

### 3. Set up the database
No MySQL needed! The app uses **SQLite by default** — zero installation required.
```bash
python manage.py migrate
python manage.py createsuperuser  # optional admin account
```

### 4. Run
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000

---

## Database Options

| Option | Setup | Best For |
|--------|-------|----------|
| **SQLite** (default) | Zero config | Local dev, testing |
| **MySQL** | Set `DB_ENGINE=django.db.backends.mysql` in `.env` | Production |

To switch to MySQL, uncomment the MySQL block in `.env` and run:
```bash
pip install mysqlclient
python manage.py migrate
```

---

## LLM Configuration

| Provider | Speed | Cost | How to enable |
|----------|-------|------|---------------|
| **Groq** | Very fast | Free (30 req/min) | Set `GROQ_API_KEY` in `.env` |
| **Ollama** | Moderate | Free (self-hosted) | Set `LLM_PROVIDER=ollama` |
| **Fallback** | Instant | Free | Auto — no API needed |

---

## Project Structure
```
feel_comfort_project/
├── feel_comfort/           # Django settings, URLs, WSGI
├── users/                  # Custom user model, auth views
├── chatbot/                # Core app
│   ├── mood_analyzer.py    # VADER + TextBlob NLP pipeline
│   ├── llm_handler.py      # Groq / Ollama / Fallback chain
│   ├── models.py           # MoodSession, UserMoodStats, DailyMoodLog
│   └── views.py            # Chat, dashboard, history endpoints
├── templates/              # HTML templates
└── static/                 # CSS, JS assets
```

## Supported Moods
sad · anxious · angry · happy · tired · confused · calm · lonely
