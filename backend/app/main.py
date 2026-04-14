from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, groups, guardian, matching, users

app = FastAPI(title="Turtle Connect API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(groups.router)
app.include_router(matching.router)
app.include_router(guardian.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
