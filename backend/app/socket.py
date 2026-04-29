import socketio
from app.database import SessionLocal
from app.models.activity import Activity
from app.models.group import Group
from app.models.message import Message
from app.models.user import User
from app.services.auth import decode_token
from app.services.safety import analyze_message

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

_sid_to_user = {}


@sio.event
async def connect(sid, environ, auth):
    token = (auth or {}).get("token")
    if not token:
        return False
    payload = decode_token(token)
    if not payload:
        return False
    _sid_to_user[sid] = int(payload["sub"])


@sio.event
async def disconnect(sid):
    _sid_to_user.pop(sid, None)


@sio.event
async def join_group(sid, data):
    await sio.enter_room(sid, f"group_{data['group_id']}")


@sio.event
async def send_message(sid, data):
    user_id = _sid_to_user.get(sid)
    if not user_id:
        return

    db = SessionLocal()
    try:
        sender = db.query(User).filter(User.id == user_id).first()
        group = db.query(Group).filter(Group.id == data["group_id"]).first()
        group_name = group.name if group else "Unknown"
        sender_name = sender.name if sender else "Unknown"

        # Run safety check
        safety = analyze_message(
            content=data["content"],
            sender_name=sender_name,
            group_name=group_name,
        )

        # Save message
        msg = Message(
            group_id=data["group_id"],
            sender_id=user_id,
            content=data["content"],
            is_flagged=safety["flagged"],
            flag_reason=safety["reason"],
        )
        db.add(msg)

        # Log message as activity
        db.add(Activity(
            user_id=user_id,
            group_id=data["group_id"],
            activity_type="message",
            duration_minutes=0,
        ))

        db.commit()
        db.refresh(msg)

        await sio.emit(
            "new_message",
            {
                "id": msg.id,
                "group_id": msg.group_id,
                "sender_id": msg.sender_id,
                "sender_name": sender_name,
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
                "is_flagged": msg.is_flagged,
            },
            room=f"group_{data['group_id']}",
        )
    finally:
        db.close()