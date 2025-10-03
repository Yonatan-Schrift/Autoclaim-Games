# 🎮 Auto Free Game Claimer

This project automates the process of claiming free games from various platforms (such as Epic Games, Gog, etc.) using browser automation via [Playwright](https://playwright.dev/).

---

## 🚀 Features

* ✅ Automatically logs into game platforms
* ✅ Locates and clicks "claim" or "purchase" buttons
* ✅ Supports multistep flows (email, password, 2FA)
* ✅ Modular design: easy to add new game sites
* ✅ Simulates human-like interactions to avoid bot detection
* ✅ Sends notifications via several channels (Discord webhook, email, etc.)
---

## 🗂️ Project Structure

```
.
├── core/               # Core automation logic (anti-bot, utils, exceptions)
├── logs/               # Log related logic + log files
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
# creates a virtual env for python, installs all requirements.
./install.bat
```

### 3. Configure credentials

Rename `user.env.example` to `user.env` and fill in your account details

Create a discord webhook for notifications and add it to the env file (optional)

### 4. Run the script

```
# uses venv and runs all current sites
./run.bat
```
OR
```
python main.py [OPTIONS]
```
     Options:
            -h, --help     Show this help message and exit
            -eg, --epic-games  Claim free games from Epic Games Store
            -pg, --prime-games Claim free games from Prime Gaming (not yet implemented)
            -gog, --gog    Claim free games from GOG (not yet implemented)
            -a, --all      Claim free games from all supported stores

---

## 🧩 Adding a New Site

1. Create a new file under `sites/` (e.g. `siteB.py`).
2. Implement the login and claim flow using Playwright locators.
3. Import it into `main.py` and add it to the workflow.

---

## ⚠️ Disclaimer

This project is for **educational purposes only**. Use responsibly. Some platforms may restrict or ban accounts that use automated tools.
