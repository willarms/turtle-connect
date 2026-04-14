# turtle-connect
Human-AI Collaboration Group Project

Instructions to run:
# Terminal 1 — backend
cd backend && venv/bin/uvicorn app.main:app --reload

# Terminal 2 — frontend
cd frontend && npm run dev

Also note that database is included in .gitignore, so any accounts stored in database locally will not persist across devices
