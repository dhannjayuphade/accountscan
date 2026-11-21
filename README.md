<div align="center">

<img src="assets/banner.svg" alt="AccountScan - by Dhananjay Uphade" width="100%"/>

<br/>

![Python](https://img.shields.io/badge/Python-3.7%2B-00ff9c?style=for-the-badge&logo=python&logoColor=white&labelColor=0b0f0c)
![License](https://img.shields.io/badge/License-MIT-00e5ff?style=for-the-badge&labelColor=0b0f0c)
![Platform](https://img.shields.io/badge/Termux%20%7C%20Linux%20%7C%20Windows%20%7C%20macOS-ff2bd6?style=for-the-badge&labelColor=0b0f0c)
![Dependencies](https://img.shields.io/badge/Dependencies-ZERO-ffd400?style=for-the-badge&labelColor=0b0f0c)
![Read Only](https://img.shields.io/badge/Mailbox-READ%20ONLY-00ff9c?style=for-the-badge&labelColor=0b0f0c)

### 🕵️ Find out **where your own email is registered** - in seconds.

**Developed by [Dhananjay Uphade](https://dhannjayuphade.github.io/)**

[🌐 Website](https://dhannjayuphade.github.io/) •
[📧 Email](mailto:dhannjayuphade5@gmail.com) •
[📸 Instagram](https://www.instagram.com/dhannjayuphade) •
[▶️ YouTube](https://youtu.be/-urVN3Hj3Bg)

</div>

---

## 📑 Table of contents

- [What is AccountScan?](#-what-is-accountscan)
- [Preview](#-preview)
- [Features](#-features)
- [⚠️ Privacy alert](#️-privacy-alert)
- [Installation (one-line commands)](#-installation-one-line-commands)
- [Get an App Password](#-get-an-app-password)
- [Usage](#-usage)
- [Uses](#-uses)
- [How it works](#-how-it-works)
- [Troubleshooting](#-troubleshooting)
- [Limits](#-limits)
- [License](#-license)
- [Developer & follow](#-developer--follow)

---

## 🔍 What is AccountScan?

Over the years you sign up on dozens of websites and apps and forget most of them.
**AccountScan** logs in to **your own mailbox** (IMAP, read-only), looks for the
emails those services sent you - *welcome*, *verify your email*, *password reset*,
*new login*, *receipt* - and builds a clean list of every service your email address
is connected to, with the date you first and last heard from them.

> 💡 Pure Python standard library. **No `pip install`, no API keys, no tracking.**

---

## 🖥️ Preview

A hacker-style terminal UI: matrix-rain intro, glitch banner, boot sequence, live
progress bars and a colour-coded results table.

```text
  >> 8 service(s) found

  ┌───┬───────────────┬────────────┬────────────┬───────┬──────────────────────────┐
  │ # │ SERVICE       │ FIRST SEEN │ LAST SEEN  │ MAILS │ TYPES                    │
  ├───┼───────────────┼────────────┼────────────┼───────┼──────────────────────────┤
  │ 1 │ flipkart.com  │ 2018-07-21 │ 2025-02-11 │    48 │ receipt,signup           │
  │ 2 │ amazon.in     │ 2018-09-02 │ 2026-10-30 │    96 │ receipt,security,signup  │
  │ 3 │ github.com    │ 2019-01-15 │ 2026-11-02 │    31 │ password,security,signup │
  │ 4 │ instagram.com │ 2019-03-04 │ 2026-08-19 │    12 │ security,signup          │
  │ 5 │ spotify.com   │ 2020-05-12 │ 2026-06-07 │     9 │ password,receipt,signup  │
  │ 6 │ canva.com     │ 2021-02-27 │ 2025-12-01 │     5 │ signup                   │
  │ 7 │ zomato.com    │ 2021-08-09 │ 2026-09-14 │    22 │ receipt,signup           │
  │ 8 │ irctc.co.in   │ 2022-01-18 │ 2026-10-03 │    14 │ password,receipt         │
  └───┴───────────────┴────────────┴────────────┴───────┴──────────────────────────┘
```

*(sample data - run `python accountscan.py --demo` to see the full animated interface without logging in)*

On small phone screens (Termux) the table automatically switches to a compact list.

---

## ✨ Features

| | Feature |
|---|---|
| 🎬 | Animated hacker UI: matrix intro, glitch banner, boot sequence, spinners, progress bars |
| 🎨 | Colour-coded results (signup / password / security / receipt) |
| 🔒 | **Read-only** IMAP access - never sends, edits or deletes mail |
| 🧠 | Smart server-side search - does not download your whole mailbox |
| 🌐 | Auto-detects Gmail, Outlook/Hotmail, Yahoo, iCloud, Zoho (or use `--host`) |
| 📅 | Shows first-seen / last-seen dates for every service |
| 📄 | Export to CSV with `--csv` |
| 📱 | Works on Termux (phone), Linux, macOS, Windows CMD / PowerShell |
| 📦 | Zero dependencies - just Python 3.7+ |
| 🛡️ | Privacy alert + ownership confirmation before every scan |

---

## ⚠️ Privacy alert

> [!WARNING]
> **Use AccountScan ONLY on a mailbox that belongs to you.**
> Accessing someone else's mailbox without permission is illegal (for example under
> the **IT Act, 2000** in India and computer-misuse laws in other countries).

- 🔑 Always log in with an **App Password** - never share your real password with any tool.
- 👁️ AccountScan is **read-only**: it opens your folder in read-only mode.
- 💻 Everything runs **locally on your device**. Nothing is uploaded, logged or sent to any server (other than your own mail provider's IMAP server).
- 🧹 Your password is only kept in memory while the program runs and is never written to disk.
- 🚫 Do **not** use it to check, track or profile other people. This tool does not support that and the author does not allow it.

---

## 📥 Installation (one-line commands)

Copy **one** line for your system, paste it, press Enter. It installs what is needed,
downloads AccountScan and opens the demo.

### 📱 Termux (Android)

```bash
pkg update -y && pkg install -y git python && git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python accountscan.py --demo
```

### 🐧 Linux - Ubuntu / Debian / Kali / Parrot

```bash
sudo apt update && sudo apt install -y git python3 && git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python3 accountscan.py --demo
```

<details>
<summary>Other Linux distros & macOS</summary>

**Fedora**
```bash
sudo dnf install -y git python3 && git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python3 accountscan.py --demo
```

**Arch / Manjaro**
```bash
sudo pacman -S --noconfirm git python && git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python accountscan.py --demo
```

**macOS (Homebrew)**
```bash
brew install git python && git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python3 accountscan.py --demo
```

</details>

### 🪟 Windows - CMD

If you already have **Git** and **Python** installed:

```bat
git clone https://github.com/dhannjayuphade/accountscan.git && cd accountscan && python accountscan.py --demo
```

Don't have them yet? Install once, **close and reopen CMD**, then run the line above:

```bat
winget install -e --id Git.Git && winget install -e --id Python.Python.3.12
```

No Git? Download just the script:

```bat
curl -L -o accountscan.py https://raw.githubusercontent.com/dhannjayuphade/accountscan/main/accountscan.py && python accountscan.py --demo
```

> 💡 For the best look on Windows use **Windows Terminal**, or run `chcp 65001` in CMD first.

### 🐍 Any system with pip (optional)

```bash
pip install git+https://github.com/dhannjayuphade/accountscan.git
```

Then simply run `accountscan --email you@gmail.com`.

### 🔄 Update

```bash
cd accountscan && git pull
```

---

## 🔑 Get an App Password

Gmail, Yahoo and iCloud do not allow your normal password for IMAP. Create an **App Password**:

| Provider | Where to create it |
|---|---|
| **Gmail** | Google Account → Security → turn on **2-Step Verification** → **App passwords** ([myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)). Make sure IMAP is enabled if your account shows that setting. |
| **Outlook / Hotmail** | Microsoft account → Security → Advanced security options → **App passwords** (needs two-step verification). If your account does not offer app passwords, Microsoft may require OAuth, which AccountScan does not support yet. |
| **Yahoo** | Account Security → **Generate app password** |
| **iCloud** | appleid.apple.com → Sign-In and Security → **App-Specific Passwords** |

---

## 🚀 Usage

**Quick start** (asks for your App Password, input is hidden):

```bash
python accountscan.py --email you@gmail.com
```

**Gmail - search your whole mailbox, from 2018, and save a CSV:**

```bash
python accountscan.py --email you@gmail.com --folder "[Gmail]/All Mail" --since 2018-01-01 --csv accounts.csv
```

**Only look for signup mails:**

```bash
python accountscan.py --email you@gmail.com --only signup
```

**See the interface without logging in:**

```bash
python accountscan.py --demo
```

### Options

| Option | Meaning |
|---|---|
| `--email` | your email address *(required for a scan)* |
| `--host` | IMAP server - auto-detected for Gmail / Outlook / Yahoo / iCloud / Zoho |
| `--folder` | mail folder, default `INBOX` |
| `--list-folders` | show your mailbox folder names and exit |
| `--since YYYY-MM-DD` | only mails after this date |
| `--only` | any of `signup` `password` `security` `receipt` |
| `--csv FILE` | also save the result as a CSV file |
| `--yes` | confirm you own the mailbox (skips the question) |
| `--demo` | run the UI with sample data, no login |
| `--about` | show developer info and exit |
| `--quick` | skip the intro animation |
| `--no-anim` / `--no-color` | turn animations / colours off |
| `--version` | show the version |

> 🔐 Tip: you can set the environment variable `MAIL_APP_PASSWORD` instead of typing the password.

---

## 🎯 Uses

- 🧹 **Digital clean-up** - find old accounts you forgot and delete the ones you don't need.
- 🛡️ **Security audit** - see which services hold your email, then enable 2FA or change passwords on the important ones.
- 💸 **Stop hidden subscriptions** - spot receipts and invoices from services you no longer use.
- 🧾 **Privacy requests** - build a list to send data-deletion requests (GDPR-style) to services.
- 🔎 **After a data breach** - cross-check the list with [Have I Been Pwned](https://haveibeenpwned.com/) for your address.
- 🗂️ **Migrating to a new email** - know every service where you must update your address.

---

## ⚙️ How it works

1. You confirm that the mailbox is yours and enter an **App Password**.
2. AccountScan connects over **SSL/TLS** and opens the folder in **read-only** mode.
3. It asks the mail server to search subjects for phrases like *welcome*, *verify your email*, *reset your password*, *new login*, *your receipt*.
4. It reads **only the headers** (From, Subject, Date) of the matches - never the mail body.
5. Senders are grouped by domain (`mail.amazon.in` → `amazon.in`) and shown with first/last dates.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Login failed` | Use an **App Password**, not your normal password. Check that IMAP is enabled. |
| `Cannot open folder` | Run `--list-folders` and use the exact name. |
| `No matching mails found` | Use `--folder "[Gmail]/All Mail"` (Gmail) or remove `--since`. |
| Boxes look broken on Windows | Use Windows Terminal or run `chcp 65001`. |
| Too slow on a huge mailbox | Add `--since 2022-01-01` or `--only signup`. |

---

## 📌 Limits

- It finds only services that **sent you an email** with a recognisable subject. Accounts that never emailed you, or mails you deleted, will not appear.
- Some services send mail through third-party senders, so the domain shown may differ from the website name.
- Subject matching is keyword-based, so a few results may be false positives.
- OAuth-only mailboxes are not supported (App Password / IMAP login only).

---

## 📜 License

Released under the **MIT License** - see [LICENSE](LICENSE).
Copyright © 2026 **Dhananjay Uphade**.

**Disclaimer:** this software is provided "as is", without warranty. You are responsible for using it lawfully and only on mailboxes you own.

---

## 👨‍💻 Developer & follow

<div align="center">

### **Dhananjay Uphade**
*Developer & creator of AccountScan*

[![Website](https://img.shields.io/badge/Website-dhannjayuphade.github.io-00ff9c?style=for-the-badge&logo=githubpages&logoColor=black&labelColor=0b0f0c)](https://dhannjayuphade.github.io/)
[![Email](https://img.shields.io/badge/Email-dhannjayuphade5%40gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dhannjayuphade5@gmail.com)

[![Instagram](https://img.shields.io/badge/Instagram-@dhannjayuphade-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/dhannjayuphade)
[![Instagram Creator Studio](https://img.shields.io/badge/Instagram-@creatorstudio__2.0-C13584?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/creatorstudio_2.0)

[![Snapchat](https://img.shields.io/badge/Snapchat-Add%20me-FFFC00?style=for-the-badge&logo=snapchat&logoColor=black)](https://www.snapchat.com/add/dhannjayuphade)
[![YouTube](https://img.shields.io/badge/YouTube-Subscribe-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/-urVN3Hj3Bg)

### 🔔 Follow • Subscribe • ⭐ Star this repo if AccountScan helped you!

</div>
