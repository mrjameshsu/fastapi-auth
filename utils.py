import logging
import smtplib
from email.message import EmailMessage

import requests

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {"User-Agent": "fastapi-auth-app/1.0 (mr.jameshsu@gmail.com)"}


def send_registration_notification(new_user_email: str) -> None:
    """Send an approval-request email to the admin when a new user registers."""
    from config import settings

    if not settings.GMAIL_USER or not settings.GMAIL_APP_PASSWORD:
        logger.warning("Email not configured — skipping registration notification.")
        return

    admin_url = f"{settings.BASE_URL}/admin"
    msg = EmailMessage()
    msg["Subject"] = f"[FastAPI Auth] New registration: {new_user_email}"
    msg["From"] = settings.GMAIL_USER
    msg["To"] = settings.ADMIN_EMAIL
    msg.set_content(
        f"A new user has registered and is waiting for approval.\n\n"
        f"  Email: {new_user_email}\n\n"
        f"Approve or reject at: {admin_url}\n"
    )
    msg.add_alternative(
        f"""<p>A new user has registered and is waiting for approval.</p>
<table>
  <tr><td><strong>Email:</strong></td><td>{new_user_email}</td></tr>
</table>
<p><a href="{admin_url}">Go to Admin Panel</a></p>""",
        subtype="html",
    )

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(settings.GMAIL_USER, settings.GMAIL_APP_PASSWORD)
            smtp.send_message(msg)
        logger.info("Registration notification sent to %s", settings.ADMIN_EMAIL)
    except Exception as exc:
        logger.error("Failed to send registration notification: %s", exc)


def geocode_address(address: str) -> tuple[float, float] | None:
    params = {"q": address, "format": "json", "limit": 1}
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=5)
        results = resp.json()
        if not results:
            return None
        return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        return None
