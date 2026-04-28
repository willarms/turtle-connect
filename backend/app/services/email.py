import asyncio

import resend

from app.config import settings


def build_report_html(data: dict) -> str:
    senior = data.get("senior_name", "Your loved one")
    total_calls = data.get("total_calls", 0)
    total_messages = data.get("total_messages", 0)
    avg_duration = data.get("avg_duration_minutes", 0)
    active_groups = data.get("active_groups", 0)
    weekly = data.get("weekly_activity", [])
    participation = data.get("group_participation", [])
    recent = data.get("recent_activity", [])

    weekly_rows = "".join(
        f"<tr><td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px'>{r['day']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px;text-align:center'>{r.get('calls',0)}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px;text-align:center'>{r.get('messages',0)}</td></tr>"
        for r in weekly
    ) or "<tr><td colspan='3' style='padding:12px;text-align:center;color:#888;font-size:16px'>No activity this week</td></tr>"

    participation_rows = "".join(
        f"<tr><td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px'>{p['name']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px;text-align:right'>{p['percentage']}%</td></tr>"
        for p in participation
    ) or "<tr><td colspan='2' style='padding:12px;text-align:center;color:#888;font-size:16px'>No group activity yet</td></tr>"

    recent_rows = "".join(
        f"<tr>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px'>{'📞' if a['type']=='call' else '💬'} {a['group']}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px;text-align:center;color:#5a7a5a;font-weight:600'>{'Call' if a['type']=='call' else 'Chat'}</td>"
        f"<td style='padding:8px 12px;border-bottom:1px solid #e8f0e8;font-size:16px;text-align:right;color:#888'>{a['duration_minutes']} min · {a['created_at'][:10]}</td>"
        f"</tr>"
        for a in recent
    ) or "<tr><td colspan='3' style='padding:12px;text-align:center;color:#888;font-size:16px'>No recent activity</td></tr>"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f5f7f5;font-family:Georgia,serif">
  <div style="max-width:600px;margin:32px auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.08)">

    <div style="background:#5a7a5a;padding:32px 32px 24px">
      <p style="margin:0 0 4px;color:#c8ddc8;font-size:14px;letter-spacing:1px;text-transform:uppercase">Turtle Connect</p>
      <h1 style="margin:0;color:white;font-size:28px;font-weight:normal">Weekly Activity Report</h1>
      <p style="margin:8px 0 0;color:#c8ddc8;font-size:18px">{senior}</p>
    </div>

    <div style="padding:32px">

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:32px">
        <div style="background:#f5f7f5;border-radius:12px;padding:20px;text-align:center">
          <p style="margin:0 0 4px;color:#888;font-size:14px">Total Calls</p>
          <p style="margin:0;font-size:36px;font-weight:bold;color:#5a7a5a">{total_calls}</p>
          <p style="margin:4px 0 0;color:#888;font-size:13px">This week</p>
        </div>
        <div style="background:#f5f7f5;border-radius:12px;padding:20px;text-align:center">
          <p style="margin:0 0 4px;color:#888;font-size:14px">Messages</p>
          <p style="margin:0;font-size:36px;font-weight:bold;color:#5a7a5a">{total_messages}</p>
          <p style="margin:4px 0 0;color:#888;font-size:13px">This week</p>
        </div>
        <div style="background:#f5f7f5;border-radius:12px;padding:20px;text-align:center">
          <p style="margin:0 0 4px;color:#888;font-size:14px">Avg Call Length</p>
          <p style="margin:0;font-size:36px;font-weight:bold;color:#5a7a5a">{avg_duration}m</p>
          <p style="margin:4px 0 0;color:#888;font-size:13px">Per call</p>
        </div>
        <div style="background:#f5f7f5;border-radius:12px;padding:20px;text-align:center">
          <p style="margin:0 0 4px;color:#888;font-size:14px">Active Groups</p>
          <p style="margin:0;font-size:36px;font-weight:bold;color:#5a7a5a">{active_groups}</p>
          <p style="margin:4px 0 0;color:#888;font-size:13px">Joined groups</p>
        </div>
      </div>

      <h2 style="font-size:18px;color:#2d3b2d;margin:0 0 12px;font-weight:600">Weekly Activity</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:32px;border:1px solid #e8f0e8;border-radius:8px;overflow:hidden">
        <thead>
          <tr style="background:#f5f7f5">
            <th style="padding:10px 12px;text-align:left;font-size:14px;color:#888;font-weight:600">Day</th>
            <th style="padding:10px 12px;text-align:center;font-size:14px;color:#888;font-weight:600">Calls</th>
            <th style="padding:10px 12px;text-align:center;font-size:14px;color:#888;font-weight:600">Messages</th>
          </tr>
        </thead>
        <tbody>{weekly_rows}</tbody>
      </table>

      <h2 style="font-size:18px;color:#2d3b2d;margin:0 0 12px;font-weight:600">Group Participation</h2>
      <table style="width:100%;border-collapse:collapse;margin-bottom:32px;border:1px solid #e8f0e8;border-radius:8px;overflow:hidden">
        <thead>
          <tr style="background:#f5f7f5">
            <th style="padding:10px 12px;text-align:left;font-size:14px;color:#888;font-weight:600">Group</th>
            <th style="padding:10px 12px;text-align:right;font-size:14px;color:#888;font-weight:600">Time Share</th>
          </tr>
        </thead>
        <tbody>{participation_rows}</tbody>
      </table>

      <h2 style="font-size:18px;color:#2d3b2d;margin:0 0 12px;font-weight:600">Recent Activity</h2>
      <table style="width:100%;border-collapse:collapse;border:1px solid #e8f0e8;border-radius:8px;overflow:hidden">
        <thead>
          <tr style="background:#f5f7f5">
            <th style="padding:10px 12px;text-align:left;font-size:14px;color:#888;font-weight:600">Group</th>
            <th style="padding:10px 12px;text-align:center;font-size:14px;color:#888;font-weight:600">Type</th>
            <th style="padding:10px 12px;text-align:right;font-size:14px;color:#888;font-weight:600">Details</th>
          </tr>
        </thead>
        <tbody>{recent_rows}</tbody>
      </table>

    </div>

    <div style="background:#f5f7f5;padding:20px 32px;text-align:center">
      <p style="margin:0;color:#aaa;font-size:13px">Turtle Connect · Weekly Guardian Report · Connect at Your Own Pace</p>
    </div>
  </div>
</body>
</html>"""

def build_group_report_html(data: dict) -> str:
    group_name = data.get("group_name", "A group")
    reason = data.get("reason", "No reason provided")
    details = data.get("details", "")

    return f"""
    <div style="font-family:Georgia,serif;padding:24px">
      <h2 style="color:#5a7a5a">Group Safety Report</h2>

      <p><strong>Group:</strong> {group_name}</p>
      <p><strong>Reason:</strong> {reason}</p>

      <p><strong>Details:</strong></p>
      <p style="background:#f5f7f5;padding:12px;border-radius:8px">
        {details if details else "No additional details provided."}
      </p>

      <hr style="margin:24px 0;border:none;border-top:1px solid #ddd"/>

      <p style="color:#888;font-size:12px">
        This report was submitted through Turtle Connect safety system.
      </p>
    </div>
    """


def _send_email_sync(to: str, subject: str, html: str) -> None:
    if not settings.resend_api_key:
        print("[email] RESEND_API_KEY not configured — skipping send")
        return
    resend.api_key = settings.resend_api_key
    resend.Emails.send({
        "from": settings.email_from,
        "to": [to],
        "subject": subject,
        "html": html,
    })


async def send_email(to: str, subject: str, html: str) -> None:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _send_email_sync, to, subject, html)
