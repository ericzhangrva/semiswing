"""Multi-channel alert dispatcher: HTML Email (SMTP) + macOS Messages SMS + ntfy.sh HTTP push + local log."""

from __future__ import annotations

import os
import smtplib
import ssl
import subprocess
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import httpx
from dotenv import load_dotenv

from semiswing.config import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")
ALERT_LOG_PATH = PROJECT_ROOT / "data" / "alerts.log"


def log_alert_locally(message: str, channel: str, status: str) -> None:
    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ALERT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] [{channel}:{status}] {message}\n")


def _is_forbidden_jhu_address(addr: str) -> bool:
    low = (addr or "").strip().lower()
    return "jhu.edu" in low or "jh.edu" in low or "jhmi.edu" in low


def send_macos_mail_html(
    subject: str,
    html_body: str,
    sender_email: str,
    recipient_email: str,
) -> bool:
    """Send an HTML email via macOS Mail.app locked strictly to `sender_email` (never default/JHU)."""
    if _is_forbidden_jhu_address(sender_email) or _is_forbidden_jhu_address(recipient_email):
        log_alert_locally(
            f"sender='{sender_email}' to='{recipient_email}'",
            "email_mail_app",
            "BLOCKED_JHU_ADDRESS",
        )
        return False

    # Write HTML body to a temporary UTF-8 file so AppleScript reads exact HTML without escaping issues
    tmp_html_path = PROJECT_ROOT / "data" / "tmp_email_body.html"
    tmp_html_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_html_path.write_text(html_body, encoding="utf-8")

    safe_subj = subject.replace("\\", "\\\\").replace('"', '\\"')
    safe_sender = sender_email.strip().replace('"', "")
    safe_recip = recipient_email.strip().replace('"', "")
    posix_path = str(tmp_html_path.resolve())

    script = f'''
    set htmlFile to POSIX file "{posix_path}"
    set htmlBody to read htmlFile as «class utf8»
    tell application "Mail"
        set matchedSender to ""
        repeat with acct in every account
            if enabled of acct is true then
                set addrList to email addresses of acct
                repeat with addr in addrList
                    set addrStr to (addr as string)
                    if addrStr is equal to "{safe_sender}" then
                        set fullName to full name of acct
                        if fullName is not missing value and fullName is not "" then
                            set matchedSender to fullName & " <" & addrStr & ">"
                        else
                            set matchedSender to addrStr
                        end if
                        exit repeat
                    end if
                end repeat
            end if
            if matchedSender is not "" then exit repeat
        end repeat

        if matchedSender is "" then
            error "Account {safe_sender} not found or not enabled in Mail.app"
        end if

        set newMsg to make new outgoing message with properties {{subject:"{safe_subj}", sender:matchedSender, visible:false}}
        tell newMsg
            make new to recipient at end of to recipients with properties {{address:"{safe_recip}"}}
            set html content to htmlBody
        end tell
        send newMsg
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=30)
        ok = res.returncode == 0
        status = "OK" if ok else f"ERR_{res.stderr.strip()}"
        log_alert_locally(
            f"from='{safe_sender}' to='{safe_recip}' subject='{subject}'",
            "email_mail_app",
            status,
        )
        return ok
    except Exception as exc:
        log_alert_locally(
            f"from='{safe_sender}' to='{safe_recip}' err='{exc}'",
            "email_mail_app",
            f"ERR_{type(exc).__name__}",
        )
        return False
    finally:
        if tmp_html_path.exists():
            try:
                tmp_html_path.unlink()
            except OSError:
                pass


def send_resend_email(
    subject: str,
    html_body: str,
    text_body: str | None,
    recipient_email: str,
    api_key: str,
) -> bool:
    """Send an HTML email from GitHub Actions / Cloud via Resend HTTP API."""
    if _is_forbidden_jhu_address(recipient_email):
        log_alert_locally(f"to='{recipient_email}'", "email_resend", "BLOCKED_JHU_ADDRESS")
        return False

    from_addr = os.getenv("RESEND_FROM", "SemiSwing Desk <onboarding@resend.dev>").strip()
    payload = {
        "from": from_addr,
        "to": [recipient_email],
        "subject": subject,
        "html": html_body,
    }
    if text_body:
        payload["text"] = text_body

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            ok = resp.status_code in (200, 201, 202)
            log_alert_locally(
                f"to='{recipient_email}' subject='{subject}'",
                "email_resend",
                "OK" if ok else f"HTTP_{resp.status_code}_{resp.text[:120]}",
            )
            return ok
    except Exception as exc:
        log_alert_locally(
            f"to='{recipient_email}' err='{exc}'",
            "email_resend",
            f"ERR_{type(exc).__name__}",
        )
        return False


def send_html_email(
    subject: str,
    html_body: str,
    text_body: str | None = None,
    recipient: str | None = None,
) -> bool:
    """Send an inline-styled HTML email via Resend API (cloud), locked macOS Mail.app, or Python SMTP."""
    import sys

    load_dotenv(PROJECT_ROOT / ".env", override=True)
    resend_key = os.getenv("RESEND_API_KEY", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587").strip() or "587")
    smtp_user = os.getenv("SMTP_USER", "").strip()
    mail_sender = os.getenv("MAIL_SENDER", "").strip()
    target_email = (recipient or os.getenv("ALERT_EMAIL", "") or mail_sender or smtp_user).strip()

    if _is_forbidden_jhu_address(mail_sender) or _is_forbidden_jhu_address(smtp_user) or _is_forbidden_jhu_address(target_email):
        log_alert_locally(
            f"subject='{subject}' to='{target_email}'",
            "email",
            "BLOCKED_JHU_ADDRESS",
        )
        return False

    # 1. Cloud HTTP Email API (Resend) when RESEND_API_KEY is configured (ideal for GitHub Actions)
    if resend_key and target_email:
        return send_resend_email(
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            recipient_email=target_email,
            api_key=resend_key,
        )

    # 2. Locked macOS Mail.app when running locally on macOS and SMTP_PASS is not set
    if sys.platform == "darwin" and mail_sender and not smtp_pass:
        return send_macos_mail_html(
            subject=subject,
            html_body=html_body,
            sender_email=mail_sender,
            recipient_email=target_email,
        )

    # 3. Direct Python SMTP
    if not smtp_user or not smtp_pass or not target_email:
        log_alert_locally(
            f"subject='{subject}' to='{target_email}'",
            "email_smtp",
            "SKIPPED_MISSING_SMTP_OR_RESEND_ENV",
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"SemiSwing Portfolio Desk <{smtp_user}>"
    msg["To"] = target_email

    fallback_text = text_body or "Please view this email in an HTML-capable email client."
    msg.attach(MIMEText(fallback_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    context = ssl.create_default_context()
    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=20) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [target_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_user, smtp_pass)
                server.sendmail(smtp_user, [target_email], msg.as_string())

        log_alert_locally(f"subject='{subject}' to='{target_email}'", "email_smtp", "OK")
        return True
    except Exception as exc:
        log_alert_locally(
            f"subject='{subject}' to='{target_email}' err='{exc}'",
            "email_smtp",
            f"ERR_{type(exc).__name__}",
        )
        return False


def send_ntfy_push(message: str, topic: str | None = None, title: str = "SemiSwing Alert") -> bool:
    """Send instant push notification via https://ntfy.sh/<topic>."""
    target_topic = topic or os.getenv("NTFY_TOPIC", "")
    if not target_topic:
        log_alert_locally(message, "ntfy", "SKIPPED_NO_TOPIC")
        return False
    url = f"https://ntfy.sh/{target_topic}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(url, content=message.encode("utf-8"), headers={"Title": title})
            ok = resp.status_code in (200, 201, 202)
            log_alert_locally(message, "ntfy", "OK" if ok else f"HTTP_{resp.status_code}")
            return ok
    except Exception as exc:
        log_alert_locally(message, "ntfy", f"ERR_{type(exc).__name__}")
        return False


def send_macos_sms(message: str, phone: str | None = None) -> bool:
    """Send SMS via macOS Messages.app AppleScript relay."""
    target_phone = phone or os.getenv("ALERT_SMS", "")
    if not target_phone:
        log_alert_locally(message, "sms_messages", "SKIPPED_NO_PHONE")
        return False

    safe_msg = message.replace('"', '\\"')
    script = f'''
    tell application "Messages"
        set targetService to 1st account whose service type = SMS
        set targetBuddy to participant "{target_phone}" of targetService
        send "{safe_msg}" to targetBuddy
    end tell
    '''
    try:
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=15)
        ok = res.returncode == 0
        log_alert_locally(message, "sms_messages", "OK" if ok else f"ERR_{res.stderr.strip()}")
        return ok
    except Exception as exc:
        log_alert_locally(message, "sms_messages", f"ERR_{type(exc).__name__}")
        return False
