from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.models.user import GuardianLink, User
from app.routers import auth, groups, guardian, matching, users
from app.services.dashboard import build_dashboard_data
from app.services.email import build_report_html, send_email

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


async def send_weekly_reports():
    db = SessionLocal()
    try:
        users_with_guardian = db.query(User).join(User.profile).filter_by(guardian_enabled=True).all()
        for senior in users_with_guardian:
            link = db.query(GuardianLink).filter_by(senior_id=senior.id).first()
            if not link:
                continue
            data = build_dashboard_data(db, senior)
            html = build_report_html(data)
            await send_email(
                to=link.guardian_email,
                subject=f"Weekly Activity Report — {senior.name}",
                html=html,
            )
    finally:
        db.close()


scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup():
    scheduler.add_job(send_weekly_reports, "cron", day_of_week="mon", hour=9, minute=0)
    scheduler.start()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


@app.get("/api/health")
def health():
    return {"status": "ok"}
