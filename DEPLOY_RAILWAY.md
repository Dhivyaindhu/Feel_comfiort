# Deploy Feel Comfort to Railway (Free)

## Prerequisites
- GitHub account: https://github.com
- Railway account: https://railway.app (sign in with GitHub — free)

---

## Step 1 — Upload your code to GitHub

Open your terminal in the project folder and run:

```bash
git init
git add .
git commit -m "Feel Comfort initial deploy"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/feel-comfort.git
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username.
> Create the repo first at https://github.com/new (name: `feel-comfort`, keep it Public)

---

## Step 2 — Deploy on Railway

1. Go to https://railway.app
2. Click **New Project**
3. Click **Deploy from GitHub repo**
4. Select your `feel-comfort` repository
5. Railway will start building automatically ✅

---

## Step 3 — Set Environment Variables

In your Railway project → click your service → **Variables** tab → add these:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | `your-secret-key-make-it-long-and-random` |
| `GROQ_API_KEY` | Your key from https://console.groq.com |
| `DEBUG` | `False` |
| `LLM_PROVIDER` | `groq` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,.railway.app` |

---

## Step 4 — Get your live URL

1. In Railway → your service → **Settings** tab
2. Scroll to **Networking → Public Networking**
3. Click **Generate Domain**
4. Your app is live at `https://your-app-name.railway.app` 🎉

---

## Updating your app later

Every time you make changes, just push to GitHub:
```bash
git add .
git commit -m "describe your change"
git push
```
Railway auto-redeploys in ~2 minutes.

---

## Important Note on SQLite

Railway's filesystem resets on every redeploy, which means **user data will be cleared** each time you push an update. This is fine for testing/demo. For a permanent production app, add a PostgreSQL database from Railway's plugin store.
