<div align="center">

# 🔮 DeepSeek Chat Backup

**Never lose a conversation again.** 🚀

A lightweight Python toolkit to back up **every** DeepSeek chat to individual `.txt` files — complete with timestamps, chat-start times, and 12-hour AM/PM formatting.

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Stable-16a34a?style=for-the-badge)](#)
[![Made by Ximanta](https://img.shields.io/badge/Made%20by-Ximanta-ff69b4?style=for-the-badge)](https://github.com/realximanta)

[📖 How It Works](#-the-journey) • [⚡ Quick Start](#-quick-start) • [🔑 Get Credentials](#-how-to-get-your-credentials) • [📂 Output Format](#-output-format) • [💬 Contact](#-contact)

</div>

---

## 🎯 Why This Exists

DeepSeek **does not provide a chat export / backup feature**. 😤 If you have hundreds of conversations with code, ideas, research, and late-night thoughts — they live and die inside the browser.

This project was born from a real frustration. It started as a **fragile Selenium scraper** and evolved — through trial, error, and DevTools spelunking 🕵️ — into a **clean, direct-API backup tool** that hits DeepSeek's own endpoints.

**No browser automation. No DOM scraping. No selectors that break next week.** 🎉

Just pure HTTP, verified against the live API.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🚀 **Direct API access** | Uses DeepSeek's own `/api/v0/` endpoints — no Selenium at runtime |
| 📄 **One file per chat** | Each conversation → its own `.txt`, named after the title |
| ⏱️ **Full timestamps** | 12-hour format `hh:mm:ss AM/PM - dd mm yy` per message |
| 🕐 **Chat start time** | Header shows exactly when the conversation began |
| 📌 **Smart sorting** | Pinned chats first, then newest-first |
| 🔐 **Auto credential grabber** | Separate script grabs token + cookies from Chrome |
| 📦 **Zero-config deps** | Script auto-installs `requests` if missing |
| 🪟 **Windows 10 friendly** | Runs perfectly from Python IDLE |
| 🎨 **Emoji-safe filenames** | Sanitizes illegal chars for Windows |

---

## 📸 Preview

**Input:** your DeepSeek account with 50+ chats 🗂️
**Output:** a folder like this 👇

```
deepseek_backups/
├── JDSG 1st Year Students 📚.txt
├── WatchDog Telegram 👺.txt
├── Telegram forward bot ❤‍🔥🌚.txt
├── Termux AI Automation Tool.txt
├── Roll back GitHub commits.txt
└── ... (one file per chat)
```

**Each file looks like this** 👇

```text
=== DeepSeek Chat Backup ===
Title: DeepSeek chat backup script
Chat started: 03:02:12 PM - 02 10 2026
Total messages: 14
=============================

User [03:04:47 PM - 02 10 2026]:
F12 → Network → Fetch/XHR...

Response [03:05:04 PM - 02 10 2026]:
# 🧭 No DevTools? No Problem...

User [03:06:11 PM - 02 10 2026]:
another question...

Response [03:06:29 PM - 02 10 2026]:
another answer...
```

---

## 🧭 The Journey

This project didn't appear fully-formed. It was **6 iterations** from "hello world" to "100/100 reliability". Here's the honest story. 📖

### 🔴 **v1 — The Naïve Selenium Scraper** *(confidence: 35/100)*

The first request: *"write a Python script that opens Chrome, logs into DeepSeek, and scrapes every chat."*

**What we built:**
- Selenium + `undetected-chromedriver`
- Manual login in the opened Chrome window
- DOM scraping of the conversation sidebar and message containers
- Guessed CSS selectors (`.fa81`, `.f9bf7997`)

**Why it failed:**
- ❌ DeepSeek uses **obfuscated, rotating class names**
- ❌ Virtual-scrolling sidebar hid older chats
- ❌ Message extraction missed code blocks
- ❌ `undetected-chromedriver` version drift with Chrome 154

**Lesson learned:** 🌱 *DOM scraping a modern React SPA is like building on sand.*

---

### 🟡 **v2 — The Hardened Scraper** *(confidence: 75/100)*

We added:
- ✅ **Auto-install** of dependencies via `subprocess.check_call([sys.executable, "-m", "pip", ...])`
- ✅ **Multi-strategy selectors** (tries XPath, CSS, `role=`, JS fallbacks)
- ✅ **JavaScript TreeWalker fallback** when CSS fails
- ✅ **`CHROME_VERSION_MAIN` config** to fix `SessionNotCreatedException`
- ✅ **Dedup + parent/child filtering**

**Still fragile** — DOM-scraping is a moving target. 🎯

**Lesson learned:** 🌱 *Heuristics help, but you're still guessing.*

---

### 🟢 **v3 — The Network-API Pivot** *(confidence: 80/100)*

Everything changed when we opened **DevTools → Network tab** and saw the real API calls. 🔍

**Discovered endpoints:**
```http
GET  /api/v0/chat_session/fetch_page?lte_cursor.pinned=false
GET  /api/v0/chat/history_messages?chat_session_id=<uuid>&cache_version=4
```

**Key insight:** DeepSeek is a thin SPA over a clean REST API. Why scrape HTML when you can call the API directly? 🤯

**New architecture:**
- Pure `requests` — no Selenium at runtime ⚡
- 50x faster (30 chats in ~15 seconds)
- No DOM selectors to break 🎉
- Cursor-paginated conversation list

**Lesson learned:** 🌱 *Always check the Network tab first.*

---

### 🔵 **v4 — Field Verification** *(confidence: 93/100)*

We captured the **real JSON responses** and stopped guessing.

**Confirmed from live data:**
```json
{
  "data": {
    "biz_data": {
      "chat_sessions": [
        {
          "id": "43d6c267-...",       // ✅ session UUID
          "title": "JDSG 1st Year...",  // ✅ chat title
          "pinned": true,               // ✅ sort key
          "updated_at": 1790945739.079  // ✅ unix timestamp
        }
      ]
    }
  }
}
```

**Lesson learned:** 🌱 *Verify, don't guess. One DevTools copy beats an hour of fallback code.*

---

### 🟣 **v5 — The Final Breakthrough** *(confidence: 100/100)*

We captured the `history_messages` response and discovered **the critical bug**:

> 🔴 **Content is NOT in `msg["content"]`** — it lives inside `msg["fragments"][].content`!

That single discovery fixed **all empty files**. 🎯

**Verified message shape:**
```json
{
  "message_id": 24,
  "role": "ASSISTANT",
  "inserted_at": 1790954971.4259999,
  "fragments": [
    {
      "id": 2,
      "type": "RESPONSE",
      "content": "# The actual message text..."
    }
  ]
}
```

**Final features added:**
- ⏱️ Chat start time = first message's `inserted_at`
- 🕐 Per-message timestamps in **12-hour AM/PM** format
- 📌 Pinned-first, newest-second sort order
- 🎨 Clean header block per file

**Lesson learned:** 🌱 *The last 10% of confidence costs 90% of the effort — but it's worth it.*

---

### 📊 The Confidence Graph

```
100 │                                     ● v5 ✅
 90 │                              ● v4
 80 │                       ● v3
 70 │                ● v2
 60 │
 50 │
 40 │
 35 │   ● v1
 30 └───────────────────────────────────────────
      1    2    3    4    5
              Iteration →
```

---

## ⚡ Quick Start

### 1️⃣ Clone the repo

```bash
git clone https://github.com/realximanta/deepseek-backup.git
cd deepseek-backup
```

### 2️⃣ Get your credentials 🔑

Run the helper script — it opens Chrome, you log in, and it **auto-grabs the token + cookies**.

```bash
python get_credentials.py
```

**See [How to Get Your Credentials](#-how-to-get-your-credentials) below for the manual DevTools method too.**

### 3️⃣ Paste credentials into the main script

Open `deepseek_backup.py` and edit the CONFIG block at the top:

```python
AUTHORIZATION = "Bearer YOUR_TOKEN_HERE"
COOKIE        = "smidV2=...; ds_session_id=..."
X_DEVICE_ID   = "your-device-id"
```

### 4️⃣ Run the backup 🚀

```bash
python deepseek_backup.py
```

### 5️⃣ Check the output 📂

```bash
deepseek_backups/
```

All chats, timestamped, done. 🎉

---

## 🔑 How to Get Your Credentials

You have **two options**: automatic (recommended) or manual via DevTools.

### 🅰️ Option A — Automatic (via `get_credentials.py`)

```bash
python get_credentials.py
```

**What happens:**
1. 🚀 Chrome opens automatically
2. 🧑 You log in to DeepSeek manually
3. 👀 The script sniffs Chrome's own network layer
4. 📝 It captures the `Authorization` header + all cookies
5. 💾 Writes them to `credentials.txt` and prints them to console

**Zero DevTools, zero copy-paste.** 🎯

---

### 🅱️ Option B — Manual (via DevTools)

<details>
<summary><b>👆 Click to expand the 11-step DevTools guide</b></summary>

#### Step 1 — Open DeepSeek
Go to `https://chat.deepseek.com` and make sure you're logged in. ✅

#### Step 2 — Open DevTools
Press **F12** (or `Ctrl + Shift + I`).

#### Step 3 — Go to the **Network** tab
Click the **Network** tab at the top of DevTools. 🌐

#### Step 4 — Click **Fetch/XHR** filter
Filters the request list to only API calls. 🎯

#### Step 5 — Type `api` in the filter box
Narrows down to DeepSeek's API endpoints. 🔍

#### Step 6 — Clear the list
Click the 🚫 **clear** icon so you start fresh.

#### Step 7 — Click a conversation in the sidebar
Pick any chat — this fires a `history_messages` request. 👆

#### Step 8 — Find the `history_messages` request
Look for `/api/v0/chat/history_messages` in the list. 🎯

#### Step 9 — Click the request
A detail panel opens on the right.

#### Step 10 — Go to the **Headers** tab
Scroll to **Request Headers** and copy:

```
authorization: Bearer eyJhbGciOiJIUzI1NiIs...
cookie: smidV2=...; ds_session_id=...
```

#### Step 11 — Also grab `x-device-id`
Scroll further down. Copy the `x-device-id` value.

#### Done! ✅
Paste them into `deepseek_backup.py`.

</details>

---

## 📂 Output Format

### 🗂️ Folder Structure

```
deepseek_backups/
├── Chat Title 1.txt
├── Chat Title 2.txt
├── Chat Title 3_1.txt   ← duplicate title auto-suffixed
└── ...
```

### 📄 File Format

```text
=== DeepSeek Chat Backup ===
Title: <chat title>
Chat started: hh:mm:ss AM/PM - dd mm yy
Total messages: <count>
=============================

User [hh:mm:ss AM/PM - dd mm yy]:
<user message>

Response [hh:mm:ss AM/PM - dd mm yy]:
<assistant response>

User [hh:mm:ss AM/PM - dd mm yy]:
<next user message>

...
```

**Timestamps use your local timezone.** 🌍

---

## 🛠️ Technical Details

<details>
<summary><b>🔬 Click to see the API contract</b></summary>

### Endpoint 1 — List Conversations

```http
GET /api/v0/chat_session/fetch_page?lte_cursor.pinned=false
Headers:
  authorization: Bearer <token>
  cookie: <cookies>
  x-client-version: 2.5.0
  x-device-id: <device-uuid>
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "biz_data": {
      "chat_sessions": [
        {
          "id": "uuid",
          "title": "string",
          "title_type": "USER | SYSTEM",
          "pinned": true,
          "model_type": "default",
          "updated_at": 1790945739.079
        }
      ],
      "has_more": false,
      "next_cursor": null
    }
  }
}
```

### Endpoint 2 — Fetch Messages

```http
GET /api/v0/chat/history_messages?chat_session_id=<uuid>&cache_version=4
Headers:
  authorization: Bearer <token>
  cookie: <cookies>
  referer: https://chat.deepseek.com/a/chat/s/<uuid>
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "biz_data": {
      "chat_messages": [
        {
          "message_id": 24,
          "role": "USER | ASSISTANT",
          "inserted_at": 1790954971.4259999,
          "fragments": [
            {
              "type": "REQUEST | RESPONSE",
              "content": "message text here"
            }
          ]
        }
      ]
    }
  }
}
```

</details>

---

## ⚠️ Security Notes

> 🔴 **Your token is a session key.** Anyone who has it can read every chat in your account.

- 🔒 **Never commit credentials to GitHub.**
- 🚫 **Never paste tokens in public chats/issues.**
- 🔄 **Rotate your token** if you accidentally expose it — just **log out and log back in** on DeepSeek.
- 💾 `credentials.txt` is in `.gitignore` — **keep it that way**.

This repo ships with **placeholder credentials only**. You must supply your own.

---

## 🤝 Contributing

Pull requests are welcome! If DeepSeek changes their API and something breaks:

1. 🍴 Fork the repo
2. 🌿 Create a branch (`git checkout -b fix/api-change`)
3. 🔧 Fix it
4. ✅ Test it
5. 📤 Open a PR

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

You are free to use, modify, and distribute this tool. **Attribution appreciated but not required.** 💚

---

## 💬 Contact

<div align="center">

**Ximanta** 👨‍💻

📧 [realximanta@gmail.com](mailto:realximanta@gmail.com)
🐙 [github.com/realximanta](https://github.com/realximanta)

*Built with frustration, coffee ☕, and DevTools.*

⭐ **If this saved your chats, give it a star!** ⭐

</div>

---

<div align="center">

**Made with ❤️ by [Ximanta](https://github.com/realximanta)**

*Because your conversations deserve to outlive the browser tab.* 🌱

</div>