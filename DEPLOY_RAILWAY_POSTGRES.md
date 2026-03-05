# Deploy Feel Comfort (PostgreSQL Version) to Railway

## What's different from the SQLite version?
- Uses **PostgreSQL** — data is permanent, never lost on redeploy
- Users stay registered, chat history is preserved forever
- Exactly the same app code — only the database is different

---

## PART 1 — Push code to GitHub

### Step 1 — Create a new GitHub repo
1. Go to https://github.com/new
2. Name it: `feel-comfort-postgres`
3. Set to **Public**
4. ❌ Do NOT add README or .gitignore
5. Click **Create repository**

### Step 2 — Push your code
Open Command Prompt in this project folder and run:

```bash
git init
git add .
git commit -m "Feel Comfort PostgreSQL version"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/feel-comfort-postgres.git
git push -u origin main
```
> Use your GitHub Personal Access Token as password when prompted
> (Create one at https://github.com/settings/tokens → repo scope)

---

## PART 2 — Create Railway Project

### Step 3 — New project from GitHub
1. Go to https://railway.app
2. Click **New Project**
3. Click **Deploy from GitHub repo**
4. Select `feel-comfort-postgres`
5. Railway starts building ✅

### Step 4 — Add PostgreSQL database
1. In your Railway project dashboard, click **+ New**
2. Select **Database → Add PostgreSQL**
3. Wait ~30 seconds for it to provision
4. Railway automatically sets `DATABASE_URL` in your app — nothing to copy!

---

## PART 3 — Set Environment Variables

### Step 5 — Add variables
Click your app service → **Variables** tab → add these:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | `feelcomfort-postgres-secret-2026-make-it-long` |
| `GROQ_API_KEY` | Your key from https://console.groq.com |
| `DEBUG` | `False` |
| `LLM_PROVIDER` | `groq` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.railway.app` |

> ✅ Do NOT add `DATABASE_URL` — Railway sets it automatically from the PostgreSQL plugin

---

## PART 4 — Go Live

### Step 6 — Generate your domain
1. Click your app service → **Settings** tab
2. Scroll to **Networking → Public Networking**
3. Click **Generate Domain**
4. Your live URL: `https://feel-comfort-postgres-XXXX.railway.app` 🎉

---

## PART 5 — Updating your app

Every time you change code:
```bash
git add .
git commit -m "what you changed"
git push
```
Railway redeploys automatically in ~2 minutes. **Your database data is never lost.**

---

## Difference Summary

| Feature | SQLite Version | PostgreSQL Version |
|---------|---------------|-------------------|
| Data after redeploy | ❌ Lost | ✅ Permanent |
| Local setup | Zero config | Needs PostgreSQL installed |
| Railway setup | Just push | Push + add DB plugin |
| Best for | Demo / Testing | Real users / Production |
