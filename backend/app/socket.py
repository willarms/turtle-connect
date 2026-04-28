import socketio
from app.database import SessionLocal
from app.models.message import Message
from app.models.user import User
from app.services.auth import decode_token

sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

# Maps socket sid -> user_id
_sid_to_user = {}


@sio.event
async def connect(sid, environ, auth):
    token = (auth or {}).get("token")
    if not token:
        return False  # reject connection
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
        msg = Message(
            group_id=data["group_id"],
            sender_id=user_id,
            content=data["content"],
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        sender = db.query(User).filter(User.id == user_id).first()
        await sio.emit(
            "new_message",
            {
                "id": msg.id,
                "group_id": msg.group_id,
                "sender_id": msg.sender_id,
                "sender_name": sender.name if sender else "Unknown",
                "content": msg.content,
                "created_at": msg.created_at.isoformat(),
            },
            room=f"group_{data['group_id']}",
        )
    finally:
        db.close()
