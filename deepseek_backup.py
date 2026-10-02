# -*- coding: utf-8 -*-
"""
DeepSeek Chat Backup — Main Script
===================================
Backs up every DeepSeek conversation to individual .txt files.
- Direct API access (no Selenium)
- Timestamps in 12-hour AM/PM format
- Chat start time in header
- Pinned-first sorting

Author : Ximanta
GitHub : https://github.com/realximanta
Email  : realximanta@gmail.com
License: MIT
"""

import subprocess, sys, os, re, time
from datetime import datetime

# ---------- AUTO-INSTALL DEPENDENCIES ----------
def _ensure(pkg):
    try:
        __import__(pkg)
    except ImportError:
        print(f"[setup] Installing '{pkg}'...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"]
        )

_ensure("requests")
import requests

# ================== CONFIG ==================
# 🔑 Paste your credentials here.
#    Run get_credentials.py to grab them automatically,
#    OR follow the DevTools guide in README.md.

AUTHORIZATION    = "Bearer YOUR_TOKEN_HERE"
COOKIE           = "smidV2=...; ds_session_id=..."
X_DEVICE_ID      = "your-device-id-here"
X_CLIENT_VERSION = "2.5.0"

OUTPUT_DIR       = "deepseek_backups"
REQUEST_DELAY    = 0.8     # seconds between requests
# ============================================

BASE = "https://chat.deepseek.com"

BASE_HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "authorization": AUTHORIZATION,
    "cookie": COOKIE,
    "origin": BASE,
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/154.0.0.0 Safari/537.36"),
    "x-client-bundle-id": "com.deepseek.chat",
    "x-client-locale": "en_US",
    "x-client-platform": "web",
    "x-client-timezone-offset": "19800",
    "x-client-version": X_CLIENT_VERSION,
    "x-device-id": X_DEVICE_ID,
}


# ---------- HELPERS ----------
def sanitize(name):
    """Make a string safe for Windows filenames."""
    name = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    name = re.sub(r"\s+", " ", name)
    return name[:120] or "Untitled"


def fmt_ts(ts):
    """Unix float → 'hh:mm:ss AM/PM - dd mm yy' (local, 12-hour)."""
    if not ts:
        return "unknown"
    try:
        dt = datetime.fromtimestamp(float(ts))
        return dt.strftime("%I:%M:%S %p - %d %m %y")
    except Exception:
        return "unknown"


def _get(path, params=None, session_id=None, retries=3):
    """GET with retries and per-request referer."""
    url = BASE + path
    headers = dict(BASE_HEADERS)
    headers["referer"] = (f"{BASE}/a/chat/s/{session_id}"
                          if session_id else BASE + "/")
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            if r.status_code == 401:
                print("\n[ERROR] 401 — token expired or invalid.")
                print("        Run get_credentials.py to refresh, or")
                print("        log out/in of DeepSeek and re-capture.")
                sys.exit(1)
            if r.status_code == 404:
                print(f"\n[ERROR] 404 on {path}")
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            print(f"  [retry {attempt+1}/{retries}] {e}")
            time.sleep(2)
    return None


# ---------- CONVERSATION LIST ----------
def list_all_conversations():
    """Fetch every conversation via cursor pagination."""
    sessions, cursor, page = [], None, 0
    while True:
        page += 1
        params = {"lte_cursor.pinned": "false"}
        if cursor:
            params["lte_cursor.cursor"] = cursor

        print(f"  Page {page} ...")
        data = _get("/api/v0/chat_session/fetch_page", params=params)
        if not data:
            break

        biz = (data.get("data") or {}).get("biz_data") or {}
        batch = biz.get("chat_sessions") or []
        if not batch:
            break

        sessions.extend(batch)
        print(f"    +{len(batch)}  (total {len(sessions)})")

        has_more = biz.get("has_more") or biz.get("has_next") or False
        cursor = (biz.get("next_cursor")
                  or biz.get("cursor")
                  or biz.get("lte_cursor"))
        if not has_more or not cursor:
            break
        time.sleep(REQUEST_DELAY)
    return sessions


# ---------- MESSAGES ----------
def get_messages(session_id):
    """Fetch message list for one conversation, sorted by message_id."""
    params = {"chat_session_id": session_id, "cache_version": "4"}
    data = _get("/api/v0/chat/history_messages",
                params=params, session_id=session_id)
    if not data:
        return []

    biz = (data.get("data") or {}).get("biz_data") or {}
    msgs = biz.get("chat_messages") or []
    try:
        msgs.sort(key=lambda m: m.get("message_id") or 0)
    except Exception:
        pass
    return msgs


def extract_content(msg):
    """
    Content lives in fragments[].content — NOT msg['content'].
    Verified against live DeepSeek API.
    """
    fragments = msg.get("fragments") or []
    parts = []
    for frag in fragments:
        if not isinstance(frag, dict):
            continue
        c = frag.get("content")
        if isinstance(c, str) and c.strip():
            parts.append(c)
    if parts:
        return "\n".join(parts)

    # Fallback (safety net)
    for k in ("content", "text", "message"):
        v = msg.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def role_label(raw):
    return "User" if str(raw).upper() == "USER" else "Response"


# ---------- SAVE ----------
def save_conversation(title, messages):
    if not messages:
        print("    [skip] no messages")
        return

    first_ts = messages[0].get("inserted_at")
    chat_started = fmt_ts(first_ts)

    safe = sanitize(title)
    path = os.path.join(OUTPUT_DIR, safe + ".txt")
    n = 1
    while os.path.exists(path):
        path = os.path.join(OUTPUT_DIR, f"{safe}_{n}.txt")
        n += 1

    written = 0
    with open(path, "w", encoding="utf-8") as f:
        f.write("=== DeepSeek Chat Backup ===\n")
        f.write(f"Title: {title}\n")
        f.write(f"Chat started: {chat_started}\n")
        f.write(f"Total messages: {len(messages)}\n")
        f.write("=" * 29 + "\n\n")

        for m in messages:
            content = extract_content(m)
            if not content.strip():
                continue
            ts = fmt_ts(m.get("inserted_at"))
            role = role_label(m.get("role", ""))
            f.write(f"{role} [{ts}]:\n{content}\n\n")
            written += 1

    if written == 0:
        os.remove(path)
        print("    [skip] 0 usable messages")
    else:
        print(f"    [saved] {os.path.basename(path)}  "
              f"({written} msg, started {chat_started})")


# ---------- MAIN ----------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("=" * 62)
    print(" DeepSeek Chat Backup — by Ximanta")
    print(" github.com/realximanta")
    print("=" * 62)

    if "YOUR_TOKEN_HERE" in AUTHORIZATION:
        print("\n[ABORT] Edit the CONFIG block — paste real credentials.")
        print("        Run get_credentials.py to grab them automatically.")
        return

    print("\n[1/2] Fetching conversation list...")
    sessions = list_all_conversations()
    if not sessions:
        print("\n[FAIL] No conversations. Token may be expired.")
        return

    # Pinned first, then newest
    pinned = [s for s in sessions if s.get("pinned")]
    normal = [s for s in sessions if not s.get("pinned")]
    pinned.sort(key=lambda s: s.get("updated_at") or 0, reverse=True)
    normal.sort(key=lambda s: s.get("updated_at") or 0, reverse=True)
    sessions = pinned + normal

    print(f"\n[OK] {len(sessions)} conversation(s) found.\n")
    print("[2/2] Backing up conversations...\n")

    for i, s in enumerate(sessions, 1):
        sid = s.get("id")
        title = s.get("title") or f"Conversation_{i}"
        pin = "[P]" if s.get("pinned") else "   "
        print(f"[{i}/{len(sessions)}] {pin} {title[:60]}")
        if not sid:
            continue
        msgs = get_messages(sid)
        print(f"    {len(msgs)} message(s)")
        save_conversation(title, msgs)
        time.sleep(REQUEST_DELAY)

    print(f"\n[DONE] → {os.path.abspath(OUTPUT_DIR)}")
    print("\n⚠️  SECURITY: Log out/in of DeepSeek to rotate the token if leaked.")


if __name__ == "__main__":
    main()