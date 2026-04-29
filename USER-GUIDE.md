# Turtle Connect — Local Setup Guide

## What You'll Need

- **Python 3.9+** — [python.org/downloads](https://www.python.org/downloads/)
- **Node.js 18+** — [nodejs.org](https://nodejs.org/)
- **Git** — [git-scm.com](https://git-scm.com/)

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/willarms/turtle-connect.git
cd turtle-connect
```

---

## Step 2 — Create the Backend Environment File

Create a file called `.env` inside the `backend/` folder:

```bash
cd backend
touch .env
```

Open it and paste in the following (fill in values from the submitted credentials document):

```
SECRET_KEY=random-key
DATABASE_URL=sqlite:///./turtle.db
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Google OAuth
GOOGLE_CLIENT_ID=<provided separately>
GOOGLE_CLIENT_SECRET=<provided separately>
GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# Resend (email)
RESEND_API_KEY=<provided separately>
EMAIL_FROM=Turtle Connect <onboarding@resend.dev>
```

> The actual key values will be submitted alongside this project. Do not commit `.env` to GitHub.

---

## Step 3 — Set Up the Backend

Open a terminal, navigate to the `backend/` folder, and run:

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Set up the database
alembic upgrade head

# Seed demo data
python seed.py
```

You should see:

```
✅ Seeded successfully!

Test accounts:
  margaret@turtle.app / password123  (Margaret Thompson)
  henry@turtle.app / password123  (Henry Kowalski)
  dorothy@turtle.app / password123  (Dorothy Nguyen)
```

> If you ever want to reset the database to a clean state, run `python seed.py --reset`

---

## Step 4 — Set Up the Frontend

Open a **second terminal** and run:

```bash
cd turtle-connect/frontend

npm install
```

---

## Step 5 — Start the App

You need **two terminals running at the same time**.

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:socket_app --reload
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Then open your browser and go to: **[http://localhost:5173](http://localhost:5173)**

---

## Step 6 — Test the Features

Log in with any of the three demo accounts (password is `password123` for all):

| Email | Name | Role |
|---|---|---|
| `margaret@turtle.app` | Margaret Thompson | Senior with guardian enabled |
| `henry@turtle.app` | Henry Kowalski | Senior |
| `dorothy@turtle.app` | Dorothy Nguyen | Senior |

### Features to explore

**Groups**
- After logging in, you'll see Margaret's groups with other members already joined
- Click any group to open the detail page

**Group Chat**
- Open *Garden Enthusiasts* or *Book Club Friends* — pre-seeded chat messages are visible
- Type a message and press Send (or Enter)

**Meeting Scheduler**
- Open *Garden Enthusiasts* — a meeting is already scheduled in 3 days
- Click *Edit* to change the time, or *+ Add to My Calendar* to open Google Calendar pre-filled

**Google Meet Link**
- Inside any group you're a member of, click *Create Meet Link* (requires Google login with calendar scope)

**Post-Meeting Safety Report**
- Click *Join Google Meet*, then switch back to the browser tab
- A "Welcome back" prompt asks how long the call was
- After logging the duration, a safety check-in form appears

**Guardian Dashboard**
- Log in as `margaret@turtle.app`
- Navigate to `/guardian` in the URL bar to view the guardian dashboard (shows call history and activity)

**Profile Setup**
- Log out, then register a brand-new account via *Sign up* to go through the onboarding flow
- Or sign in with a Google account to be routed to setup automatically on first login

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` on backend start | Make sure the venv is activated: `source venv/bin/activate` |
| Frontend opens on port 5174 instead of 5173 | Something else is using 5173. Either close it or update `GOOGLE_REDIRECT_URI` in `.env` to use 5174 |
| Google sign-in says "not available" | The `.env` file is missing or `GOOGLE_CLIENT_ID` is empty |
| Database errors on start | Run `alembic upgrade head` to make sure migrations are applied |
| Want to start fresh | Run `python seed.py --reset` from the `backend/` folder |

**If Problems Persist**
- Feel free to reach out to any of us with questions while grading, thanks!
