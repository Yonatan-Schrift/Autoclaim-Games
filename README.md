# 🎮 Auto Free Game Claimer

This project automates the process of claiming free games from various platforms (such as Epic Games, Gog, etc.) using browser automation via [Playwright](https://playwright.dev/).

---

## 🚀 Features

* ✅ Automatically logs into game platforms
* ✅ Locates and clicks "claim" or "purchase" buttons
* ✅ Supports multi-step flows (email, password, 2FA)
* ✅ Modular design: easy to add new game sites
* ✅ Simulates human-like interactions to avoid bot detection

---

## 🗂️ Project Structure

```
.
├── core/               # Core automation logic (anti-bot, utils, exceptions)
├── sites/              # Platform-specific logic (e.g. Epic, Gog)
├── main.py             # Entry point
├── user.env.example    # Environment variables template (credentials)
├── requirements.txt    # Python dependencies
```

---

## ⚙️ Setup

### 1. Clone the repo

```
git clone https://github.com/Yonatan-Schrift/Autoclaim-Games
cd Autoclaim-Games
```
OR
```
download manually the code from github
extract the zip
open the extracted folder
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Configure credentials

Copy `user.env.example` to `user.env` and fill in your account details:

```
cp user.env.example user.env
```

### 4. Run the script

```
python main.py
```

---

## 🧩 Adding a New Site

1. Create a new file under `sites/` (e.g. `siteB.py`).
2. Implement the login and claim flow using Playwright locators.
3. Import it into `main.py` and add it to the workflow.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Use responsibly. Some platforms may restrict or ban accounts that use automated tools.
