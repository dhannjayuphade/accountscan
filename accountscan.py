#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AccountScan - find which websites/services your OWN email address is registered on.

Developer : Dhananjay Uphade
Website   : https://dhannjayuphade.github.io/
License   : MIT

It logs in to YOUR mailbox over IMAP (read-only), looks for signup /
verification / password-reset / security / receipt emails and groups them by
sender domain. Pure Python standard library: no pip install needed.

Use it ONLY on a mailbox that belongs to you.
"""
import argparse
import csv
import getpass
import html as _html
import imaplib
import os
import random
import re
import shutil
import sys
import textwrap
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.utils import parseaddr, parsedate_to_datetime

__version__ = "1.0.0"
NAME = "AccountScan"
DEV = "Dhananjay Uphade"
SITE = "https://dhannjayuphade.github.io/"
LINKS = [
    ("Website", SITE),
    ("Email", "dhannjayuphade5@gmail.com"),
    ("Instagram", "https://www.instagram.com/dhannjayuphade"),
    ("Creator IG", "https://www.instagram.com/creatorstudio_2.0"),
    ("Snapchat", "https://www.snapchat.com/add/dhannjayuphade"),
    ("YouTube", "https://youtu.be/-urVN3Hj3Bg"),
]

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------
HOSTS = {
    "gmail.com": "imap.gmail.com",
    "googlemail.com": "imap.gmail.com",
    "outlook.com": "outlook.office365.com",
    "hotmail.com": "outlook.office365.com",
    "live.com": "outlook.office365.com",
    "yahoo.com": "imap.mail.yahoo.com",
    "yahoo.in": "imap.mail.yahoo.com",
    "icloud.com": "imap.mail.me.com",
    "zoho.com": "imap.zoho.com",
}

KEYWORDS = {
    "signup": ["welcome", "verify your email", "confirm your email",
               "confirm your account", "activate your account",
               "verification code", "your account has been created",
               "thanks for signing up", "thank you for registering"],
    "password": ["reset your password", "password reset", "password changed"],
    "security": ["new login", "new sign-in", "security alert", "new device"],
    "receipt": ["your receipt", "order confirmation", "your invoice",
                "payment received"],
}

TYPE_COLOR = {"signup": 46, "password": 220, "security": 203, "receipt": 51}

FREE_MAIL = {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com",
             "yahoo.com", "yahoo.in", "icloud.com", "live.com", "proton.me"}
SLD = {"co", "com", "org", "net", "gov", "ac", "edu", "nic"}

# Platform name + the page where YOU manage your own account (settings / login).
SERVICE_INFO = {
    "google.com": ("Google", "https://myaccount.google.com/"),
    "youtube.com": ("YouTube", "https://www.youtube.com/account"),
    "instagram.com": ("Instagram", "https://www.instagram.com/accounts/edit/"),
    "facebook.com": ("Facebook", "https://www.facebook.com/settings"),
    "facebookmail.com": ("Facebook", "https://www.facebook.com/settings"),
    "snapchat.com": ("Snapchat", "https://accounts.snapchat.com/"),
    "snap.com": ("Snapchat", "https://accounts.snapchat.com/"),
    "x.com": ("X (Twitter)", "https://x.com/settings/account"),
    "twitter.com": ("X (Twitter)", "https://x.com/settings/account"),
    "linkedin.com": ("LinkedIn", "https://www.linkedin.com/psettings/"),
    "github.com": ("GitHub", "https://github.com/settings/profile"),
    "telegram.org": ("Telegram", "https://my.telegram.org/"),
    "discord.com": ("Discord", "https://discord.com/channels/@me"),
    "reddit.com": ("Reddit", "https://www.reddit.com/settings/account"),
    "redditmail.com": ("Reddit", "https://www.reddit.com/settings/account"),
    "pinterest.com": ("Pinterest", "https://www.pinterest.com/settings/"),
    "spotify.com": ("Spotify", "https://www.spotify.com/account/"),
    "netflix.com": ("Netflix", "https://www.netflix.com/YourAccount"),
    "amazon.in": ("Amazon India", "https://www.amazon.in/gp/css/homepage.html"),
    "amazon.com": ("Amazon", "https://www.amazon.com/gp/css/homepage.html"),
    "flipkart.com": ("Flipkart", "https://www.flipkart.com/account/"),
    "microsoft.com": ("Microsoft", "https://account.microsoft.com/"),
    "apple.com": ("Apple", "https://appleid.apple.com/"),
    "canva.com": ("Canva", "https://www.canva.com/settings"),
    "zomato.com": ("Zomato", "https://www.zomato.com/"),
    "swiggy.in": ("Swiggy", "https://www.swiggy.com/"),
    "paytm.com": ("Paytm", "https://paytm.com/"),
    "irctc.co.in": ("IRCTC", "https://www.irctc.co.in/nget/train-search"),
}


def service_info(dom):
    """Return (platform name, link). Unknown domains fall back to the site itself."""
    if dom in SERVICE_INFO:
        return SERVICE_INFO[dom]
    return dom.split(".")[0].capitalize(), f"https://{dom}/"

DEMO_ROWS = [
    ("flipkart.com", "2018-07-21", "2025-02-11", 48, "receipt,signup"),
    ("amazon.in", "2018-09-02", "2026-10-30", 96, "receipt,security,signup"),
    ("github.com", "2019-01-15", "2026-11-02", 31, "password,security,signup"),
    ("instagram.com", "2019-03-04", "2026-08-19", 12, "security,signup"),
    ("spotify.com", "2020-05-12", "2026-06-07", 9, "password,receipt,signup"),
    ("canva.com", "2021-02-27", "2025-12-01", 5, "signup"),
    ("zomato.com", "2021-08-09", "2026-09-14", 22, "receipt,signup"),
    ("irctc.co.in", "2022-01-18", "2026-10-03", 14, "password,receipt"),
]

# --------------------------------------------------------------------------
# Terminal helpers (colors, animation)
# --------------------------------------------------------------------------
COLOR = True
ANIM = True

GREEN, DGREEN, CYAN, RED, YELLOW, GREY, MAG, WHITE = 46, 34, 51, 196, 226, 244, 201, 255


def C(n, text, bold=False):
    """Wrap text in a 256-colour ANSI code (no-op when colour is off)."""
    if not COLOR:
        return str(text)
    b = "1;" if bold else ""
    return f"\033[{b}38;5;{n}m{text}\033[0m"


def setup_terminal():
    if os.name == "nt":
        os.system("")  # enables ANSI escape support in Windows 10+ cmd
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def term_width(default=80):
    return shutil.get_terminal_size((default, 24)).columns


def pause(t):
    if ANIM:
        time.sleep(t)


def type_out(text, delay=0.01):
    if not ANIM:
        print(text)
        return
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\n")


def status(sym, color, text):
    print(f"  {C(GREY, '[')}{C(color, sym, True)}{C(GREY, ']')} {text}")


def fail(msg):
    status("x", RED, C(RED, msg))
    sys.exit(1)


def with_spinner(label, fn):
    """Run fn() while a small spinner animates (needs a real terminal)."""
    if not ANIM:
        return fn()
    stop = threading.Event()

    def run():
        frames = "|/-\\"
        i = 0
        while not stop.is_set():
            sys.stdout.write(f"\r  {C(CYAN, frames[i % 4], True)} {label}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.08)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    try:
        return fn()
    finally:
        stop.set()
        t.join()
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()


def show_progress(label, done, total, width=26):
    pct = (done / total) if total else 1.0
    if COLOR:
        filled = int(width * pct)
        bar = "█" * filled + "░" * (width - filled)
        sys.stdout.write(f"\r  {C(GREY, label.ljust(10))} {C(CYAN, bar)} "
                         f"{int(pct * 100):3d}% {C(GREY, f'({done}/{total})')}")
        sys.stdout.flush()
        if done >= total:
            sys.stdout.write("\n")
    elif done >= total:
        print(f"  {label}: {done}/{total}")


def matrix_intro(frames=14, height=8):
    """Short 'matrix rain' animation before the banner."""
    if not ANIM:
        return
    w = min(term_width(), 80) - 1
    chars = "01abcdef#$%&*+<>[]{}/\\|=~"
    for _ in range(frames):
        lines = []
        for _r in range(height):
            row = "".join(random.choice(chars) if random.random() < 0.33 else " "
                          for _ in range(w))
            lines.append(C(random.choice([22, 28, 34, 40, 46]), row))
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.write(f"\033[{height}A")
        sys.stdout.flush()
        time.sleep(0.07)
    sys.stdout.write("\033[2K\n" * height + f"\033[{height}A")
    sys.stdout.flush()


# --------------------------------------------------------------------------
# Banner
# --------------------------------------------------------------------------
GLYPHS = {
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "C": [" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"],
    "O": [" ██████╗ ", "██╔═══██╗", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "U": ["██╗   ██╗", "██║   ██║", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "],
    "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"],
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "S": ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"],
}


def render_word(word):
    rows = [""] * 6
    for ch in word:
        g = GLYPHS[ch]
        wdt = max(len(x) for x in g)
        rows = [rows[i] + g[i].ljust(wdt) for i in range(6)]
    return rows


def banner():
    tw = term_width()
    print()
    if tw >= 64:
        for word, pal in (("ACCOUNT", (46, 46, 40, 40, 34, 28)),
                          ("SCAN", (51, 45, 39, 38, 32, 31))):
            for i, line in enumerate(render_word(word)):
                print("  " + C(pal[i], line))
                pause(0.035)
    else:
        inner = f" {NAME.upper()} "
        w = len(inner) + 8
        print(C(46, "  ╔" + "═" * w + "╗"))
        print(C(46, "  ║") + C(CYAN, inner.center(w), True) + C(46, "║"))
        print(C(46, "  ╚" + "═" * w + "╝"))
    print()
    type_out("  " + C(CYAN, ">> ", True) + C(WHITE, "Find where YOUR email is registered", True), 0.012)
    print("  " + C(GREY, f"v{__version__}") + C(DGREEN, "  |  ") + C(GREY, "by ")
          + C(MAG, DEV, True))
    print("  " + C(GREY, SITE))
    print()


def footer():
    w = min(term_width(), 72) - 4
    print()
    print("  " + C(DGREEN, "─" * w))
    print(f"  {C(MAG, '>> DEVELOPER', True)}  {C(WHITE, DEV, True)}")
    for label, url in LINKS:
        print(f"  {C(GREY, label.ljust(10))} {C(CYAN, url)}")
    print()
    print("  " + C(YELLOW, "Follow & subscribe if this tool helped you!", True))
    print("  " + C(DGREEN, "─" * w))
    print()


def box(title, lines, border=RED, title_color=YELLOW):
    w = min(term_width(), 76) - 4
    inner = w - 2
    head = f" {title} "
    print("  " + C(border, "╔", True) + C(title_color, head, True)
          + C(border, "═" * max(inner - len(head), 0) + "╗", True))
    for line in lines:
        wrapped = textwrap.wrap(line, inner - 2) or [""]
        for k, part in enumerate(wrapped):
            prefix = "" if k == 0 else "  "
            text = (" " + prefix + part).ljust(inner)
            print("  " + C(border, "║", True) + C(252, text) + C(border, "║", True))
    print("  " + C(border, "╚" + "═" * inner + "╝", True))


def privacy_alert():
    box("[!] PRIVACY ALERT", [
        "- Use this tool ONLY on a mailbox that belongs to YOU.",
        "- Scanning someone else's mailbox is illegal (IT Act 2000 in India "
        "and computer-misuse laws elsewhere).",
        "- Log in with an APP PASSWORD. Never share your real password.",
        "- Read-only: AccountScan never sends, edits or deletes any mail.",
        "- Everything is processed locally. Nothing is uploaded anywhere.",
    ])
    print()


def boot():
    steps = ["Loading modules", "Arming read-only mode",
             "Preparing secure IMAP (SSL/TLS) channel",
             "Local processing only - no data leaves this device"]
    for s in steps:
        sys.stdout.write(f"  {C(GREY, '[')}{C(GREEN, '*', True)}{C(GREY, ']')} {s} ")
        sys.stdout.flush()
        if ANIM:
            for ch in "|/-\\|/-\\":
                sys.stdout.write(C(CYAN, ch) + "\b")
                sys.stdout.flush()
                time.sleep(0.05)
        sys.stdout.write(C(GREEN, "OK", True) + "\n")
    print()


# --------------------------------------------------------------------------
# Mail logic
# --------------------------------------------------------------------------
def base_domain(host):
    parts = host.lower().strip(".").split(".")
    if len(parts) >= 3 and len(parts[-1]) == 2 and parts[-2] in SLD:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def dec(value):
    try:
        return str(make_header(decode_header(value or "")))
    except Exception:
        return value or ""


def imap_date(s):
    return datetime.strptime(s, "%Y-%m-%d").strftime("%d-%b-%Y")


def to_naive_utc(d):
    """Make every date comparable (some headers have tz, some don't)."""
    if d is not None and d.tzinfo is not None:
        d = d.astimezone(timezone.utc).replace(tzinfo=None)
    return d


def find_ids(conn, since, kinds, on_step=None):
    """Server-side search, so the whole mailbox is never downloaded."""
    ids = {}
    jobs = [(k, kw) for k in kinds for kw in KEYWORDS[k]]
    for n, (kind, kw) in enumerate(jobs, 1):
        crit = []
        if since:
            crit += ["SINCE", imap_date(since)]
        crit += ["SUBJECT", f'"{kw}"']
        typ, data = conn.search(None, *crit)
        if typ == "OK" and data and data[0]:
            for i in data[0].split():
                ids.setdefault(i, kind)
        if on_step:
            on_step(n, len(jobs))
    return ids


def fetch_headers(conn, ids, batch=200, on_step=None):
    out = []
    id_list = list(ids)
    total = len(id_list)
    for n in range(0, total, batch):
        chunk = id_list[n:n + batch]
        typ, data = conn.fetch(
            b",".join(chunk), "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        if typ == "OK":
            for item in data:
                if isinstance(item, tuple):
                    out.append(message_from_bytes(item[1]))
        if on_step:
            on_step(min(n + batch, total), total)
    return out


def summarize(msgs):
    sites = defaultdict(lambda: {"count": 0, "first": None, "last": None,
                                 "types": set(), "subject": ""})
    for m in msgs:
        addr = parseaddr(dec(m["From"]))[1]
        if "@" not in addr:
            continue
        dom = base_domain(addr.split("@")[-1])
        if dom in FREE_MAIL:
            continue
        try:
            d = to_naive_utc(parsedate_to_datetime(m["Date"]))
        except Exception:
            d = None
        s = sites[dom]
        s["count"] += 1
        subj = dec(m["Subject"]).replace("\n", " ").replace("\r", " ")
        low = subj.lower()
        for kind, kws in KEYWORDS.items():
            if any(k in low for k in kws):
                s["types"].add(kind)
        if d:
            if not s["first"] or d < s["first"]:
                s["first"], s["subject"] = d, subj[:60]
            if not s["last"] or d > s["last"]:
                s["last"] = d
    rows = []
    for dom, s in sites.items():
        rows.append({
            "service": dom,
            "first": s["first"].strftime("%Y-%m-%d") if s["first"] else "?",
            "last": s["last"].strftime("%Y-%m-%d") if s["last"] else "?",
            "count": s["count"],
            "types": ",".join(sorted(s["types"])),
            "subject": s["subject"],
            "name": service_info(dom)[0],
            "link": service_info(dom)[1],
        })
    rows.sort(key=lambda r: (r["first"] == "?", r["first"]))
    return rows


# --------------------------------------------------------------------------
# Results output
# --------------------------------------------------------------------------
def color_types(types):
    parts = [t for t in types.split(",") if t]
    return ",".join(C(TYPE_COLOR.get(t, GREY), t) for t in parts)


def print_results(rows):
    print()
    if not rows:
        status("!", YELLOW, "No matching mails found. Try --folder, --since or a different mailbox folder.")
        return
    headers = ["#", "SERVICE", "FIRST SEEN", "LAST SEEN", "MAILS", "TYPES"]
    data = []
    for i, r in enumerate(rows, 1):
        svc = r["service"] if len(r["service"]) <= 28 else r["service"][:27] + "~"
        data.append([str(i), svc, r["first"], r["last"], str(r["count"]), r["types"]])
    widths = [max(len(headers[c]), *(len(row[c]) for row in data)) for c in range(6)]
    table_w = sum(widths) + 3 * 6 + 1

    print("  " + C(GREEN, f">> {len(rows)} service(s) found", True))
    print()
    if term_width() >= table_w + 2:
        def line(l, m, r):
            return "  " + C(DGREEN, l + m.join("─" * (w + 2) for w in widths) + r)

        print(line("┌", "┬", "┐"))
        cells = [C(CYAN, headers[c].ljust(widths[c]), True) for c in range(6)]
        sep = C(DGREEN, "│")
        print("  " + sep + (" " + (" " + sep + " ").join(cells) + " ") + sep)
        print(line("├", "┼", "┤"))
        for row in data:
            plain_types = row[5]
            cells = [
                C(GREY, row[0].rjust(widths[0])),
                C(GREEN, row[1].ljust(widths[1]), True),
                row[2].ljust(widths[2]),
                row[3].ljust(widths[3]),
                C(YELLOW, row[4].rjust(widths[4])),
                color_types(plain_types) + " " * (widths[5] - len(plain_types)),
            ]
            print("  " + sep + (" " + (" " + sep + " ").join(cells) + " ") + sep)
        print(line("└", "┴", "┘"))
    else:  # narrow screens (phones): compact list
        for row in data:
            print(f"  {C(GREY, row[0].rjust(3))} {C(GREEN, row[1], True)}")
            print(f"      {C(GREY, row[2])} -> {C(GREY, row[3])}  "
                  f"{C(YELLOW, row[4])} mail(s)")
            print(f"      {color_types(row[5])}")

    print()
    print("  " + C(MAG, ">> YOUR ACCOUNTS (open to manage / secure / delete)", True))
    for i, r in enumerate(rows, 1):
        name = r.get("name") or service_info(r["service"])[0]
        link = r.get("link") or service_info(r["service"])[1]
        print(f"  {C(GREY, str(i).rjust(3))} {C(GREEN, name.ljust(14), True)} {C(CYAN, link)}")
    print()
    print("  " + C(GREY, "Links open the service's own account page. Email headers do not "
                         "contain your username, so exact profile URLs cannot be known."))


def save_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["platform", "service", "link", "first_seen", "last_seen",
                    "mails", "types", "first_subject"])
        for r in rows:
            w.writerow([r.get("name", ""), r["service"], r.get("link", ""),
                        r["first"] if r["first"] != "?" else "",
                        r["last"] if r["last"] != "?" else "", r["count"],
                        "|".join(r["types"].split(",")), r["subject"]])
    status("+", GREEN, f"Saved CSV: {C(CYAN, path)}")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def build_parser():
    ap = argparse.ArgumentParser(
        prog="accountscan",
        description=f"{NAME} v{__version__} - list the services your OWN email "
                    f"is registered on. By {DEV} ({SITE})")
    ap.add_argument("--email", help="your email address")
    ap.add_argument("--host", help="IMAP server (auto-detected for common providers)")
    ap.add_argument("--folder", default="INBOX",
                    help='mail folder (Gmail: "[Gmail]/All Mail" searches everything)')
    ap.add_argument("--since", help="only mails since YYYY-MM-DD")
    ap.add_argument("--only", nargs="+", choices=list(KEYWORDS),
                    default=list(KEYWORDS), help="which mail types to look for")
    ap.add_argument("--csv", help="also save the result to this CSV file")
    ap.add_argument("--list-folders", action="store_true",
                    help="show the folder names of your mailbox and exit")
    ap.add_argument("--watch", action="store_true",
                    help="Security Watch: find unknown logins / hacked-account alerts")
    ap.add_argument("--days", type=int, default=30,
                    help="Security Watch: how many days back to check (default 30)")
    ap.add_argument("--yes", action="store_true",
                    help="confirm that you own this mailbox (skips the question)")
    ap.add_argument("--demo", action="store_true",
                    help="show the interface with sample data (no login)")
    ap.add_argument("--about", action="store_true",
                    help="show developer info and exit")
    ap.add_argument("--quick", action="store_true", help="skip the intro animation")
    ap.add_argument("--no-anim", action="store_true", help="turn animations off")
    ap.add_argument("--no-color", action="store_true", help="turn colours off")
    ap.add_argument("--version", action="version", version=f"{NAME} {__version__}")
    return ap


def confirm_ownership(yes):
    if yes:
        return
    if not sys.stdin.isatty():
        fail("Non-interactive run: pass --yes to confirm you own this mailbox.")
    ans = input("  " + C(YELLOW, "Do you OWN this mailbox and agree to use it lawfully? [y/N] ", True))
    if ans.strip().lower() not in ("y", "yes"):
        fail("Cancelled. AccountScan only works on your own mailbox.")
    print()


def list_folders(conn):
    typ, data = conn.list()
    print()
    status("+", GREEN, "Folders in your mailbox:")
    for raw in data or []:
        if not raw:
            continue
        line = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else str(raw)
        m = re.match(r'\((?P<flags>.*?)\)\s+"?(?P<delim>[^"\s]*)"?\s+(?P<name>.*)', line)
        name = (m.group("name") if m else line).strip().strip('"')
        print("    " + C(CYAN, name))


def clear_screen():
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()


# --------------------------------------------------------------------------
# Security Watch: detect unauthorized logins on YOUR accounts
# --------------------------------------------------------------------------
WATCH_WORDS = {
    "HIGH": ["password changed", "password was changed", "password has been changed",
             "recovery email", "recovery phone", "recovery information",
             "2-step verification turned off", "turned off 2-step",
             "suspicious", "unusual", "blocked", "was not you", "someone else"],
    "MEDIUM": ["new login", "new sign-in", "new sign in", "new device",
               "security alert", "sign-in attempt", "login attempt",
               "signed in to", "logged in from"],
}

CHECK_LINKS = [
    ("Google: devices signed in (log out here)", "https://myaccount.google.com/device-activity"),
    ("Google: security checkup", "https://myaccount.google.com/security-checkup"),
    ("Google: FIND / LOCK / ERASE a lost phone", "https://myaccount.google.com/find-your-phone"),
    ("Microsoft: recent sign-in activity", "https://account.live.com/activity"),
    ("Apple ID: devices", "https://appleid.apple.com/"),
    ("Facebook: security & login", "https://www.facebook.com/settings?tab=security"),
    ("Have I Been Pwned: is my email in a breach?", "https://haveibeenpwned.com/"),
]

DEVICE_RE = re.compile(
    r"\b(Windows(?: NT)?(?: [\d.]+)?|Mac OS X|macOS|iPhone|iPad|Android(?: [\d.]+)?|"
    r"Linux|Ubuntu|ChromeOS|Chrome|Firefox|Safari|Edge|Opera|Samsung|Pixel|Xiaomi|"
    r"Redmi|OnePlus|Vivo|Oppo|Realme)\b", re.I)
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
LOC_RE = re.compile(r"(?:Location|Near|Approximate location|City)\s*[:\-]\s*([^\r\n<]{3,60})", re.I)


def msg_text(m):
    """Best-effort readable text of a message (plain preferred, else stripped HTML)."""
    plain, htm = "", ""
    for part in m.walk():
        ctype = part.get_content_type()
        if ctype not in ("text/plain", "text/html"):
            continue
        try:
            raw = part.get_payload(decode=True) or b""
            txt = raw.decode(part.get_content_charset() or "utf-8", "replace")
        except Exception:
            continue
        if ctype == "text/plain":
            plain += txt + "\n"
        else:
            htm += txt + "\n"
    if plain.strip():
        return plain
    htm = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", htm)
    htm = _html.unescape(re.sub(r"<[^>]+>", "\n", htm))
    return re.sub(r"\n\s*\n+", "\n", htm)


def parse_event(m):
    subj = dec(m["Subject"]).replace("\n", " ").replace("\r", " ")
    body = msg_text(m)
    low_subj = subj.lower()
    low_mix = (subj + " " + body[:800]).lower()
    risk = "LOW"
    if any(k in low_mix for k in WATCH_WORDS["HIGH"]):
        risk = "HIGH"
    elif any(k in low_subj for k in WATCH_WORDS["MEDIUM"]):
        risk = "MEDIUM"
    addr = parseaddr(dec(m["From"]))[1]
    dom = base_domain(addr.split("@")[-1]) if "@" in addr else "?"
    try:
        d = to_naive_utc(parsedate_to_datetime(m["Date"]))
    except Exception:
        d = None
    head = body[:3000]
    ips = [ip for ip in dict.fromkeys(IP_RE.findall(head))
           if all(int(x) <= 255 for x in ip.split("."))][:2]
    devs = list(dict.fromkeys(x.strip().title() for x in DEVICE_RE.findall(head)))[:3]
    loc = LOC_RE.search(head)
    details = []
    if devs:
        details.append("Device: " + ", ".join(devs))
    if ips:
        details.append("IP: " + ", ".join(ips))
    if loc:
        details.append("Location: " + loc.group(1).strip())
    return {"date": d, "service": dom, "subject": subj[:70], "risk": risk,
            "details": details}


def watch_mode(conn, args):
    days = args.days
    since = args.since or (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    print("  " + C(MAG, f">> SECURITY WATCH  (since {since})", True))
    print("  " + C(GREY, "Looking for login / device / password alerts in YOUR mailbox..."))
    print()
    words = WATCH_WORDS["HIGH"] + WATCH_WORDS["MEDIUM"]
    ids = {}
    for n, kw in enumerate(words, 1):
        typ, data = conn.search(None, "SINCE", imap_date(since), "SUBJECT", f'"{kw}"')
        if typ == "OK" and data and data[0]:
            for i in data[0].split():
                ids[i] = 1
        show_progress("Searching", n, len(words))
    id_list = sorted(ids, key=int)[-80:]
    status("+", GREEN, f"{len(ids)} security mail(s) found" +
           (" (showing newest 80)" if len(ids) > 80 else ""))

    events = []
    for n in range(0, len(id_list), 20):
        chunk = id_list[n:n + 20]
        typ, data = conn.fetch(b",".join(chunk), "(BODY.PEEK[])")
        if typ == "OK":
            for item in data:
                if isinstance(item, tuple):
                    events.append(parse_event(message_from_bytes(item[1])))
        show_progress("Reading", min(n + 20, len(id_list)), len(id_list))

    events.sort(key=lambda e: (e["date"] is None, e["date"] or datetime.min), reverse=False)
    events.sort(key=lambda e: e["date"] or datetime.min, reverse=True)
    print()
    colors = {"HIGH": RED, "MEDIUM": YELLOW, "LOW": GREY}
    for e in events:
        when = e["date"].strftime("%Y-%m-%d %H:%M") if e["date"] else "unknown date"
        tag = C(colors[e["risk"]], f"[{e['risk']}]".ljust(8), True)
        print(f"  {tag} {C(GREY, when)}  {C(GREEN, e['service'], True)}")
        print(f"           {e['subject']}")
        if e["details"]:
            print("           " + C(CYAN, "  |  ".join(e["details"])))
    if events:
        print()

    high = sum(1 for e in events if e["risk"] == "HIGH")
    med = sum(1 for e in events if e["risk"] == "MEDIUM")
    if high:
        box("[!] ACT NOW - POSSIBLE UNAUTHORIZED ACCESS", [
            f"{high} high-risk alert(s) found. If you did NOT do these, your account may be hacked.",
            "1. Change that account's password from a device you trust.",
            "2. Open the device page below and LOG OUT all unknown devices.",
            "3. Check the recovery email/phone were not changed. Turn on 2-Step Verification.",
            "4. If your phone is lost or stolen: use 'Find my phone' below to lock or erase it.",
        ], border=RED)
    elif med:
        box("[i] REVIEW THESE LOGINS", [
            f"{med} login/device alert(s). If you recognise the device and time, ignore it.",
            "If not, change the password and log out that device using the links below.",
        ], border=YELLOW, title_color=YELLOW)
    else:
        box("[+] NOTHING FOUND", [
            "No security alerts in this period.",
            "Note: a hacker can delete alert mails, so also check the device lists below.",
        ], border=GREEN, title_color=GREEN)
    print()
    print("  " + C(MAG, ">> CHECK / LOG OUT DEVICES (open these on your phone)", True))
    for label, url in CHECK_LINKS:
        print(f"  {C(GREEN, label)}")
        print(f"     {C(CYAN, url)}")
    print()
    if args.csv and events:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["risk", "date_utc", "service", "subject", "details"])
            for e in events:
                w.writerow([e["risk"], e["date"].strftime("%Y-%m-%d %H:%M") if e["date"] else "",
                            e["service"], e["subject"], " | ".join(e["details"])])
        status("+", GREEN, f"Saved CSV: {C(CYAN, args.csv)}")


def ask_mode():
    print("  " + C(MAG, "Choose a mode:", True))
    print("   " + C(GREEN, "[1]", True) + " Find my accounts  (where is my email registered)")
    print("   " + C(GREEN, "[2]", True) + " Security watch   (detect hacked / unknown logins, lost phone)")
    while True:
        try:
            v = input("  " + C(CYAN, ">> ", True) + "Select 1 or 2 [1]: ").strip()
        except EOFError:
            return False
        if v in ("", "1"):
            print()
            return False
        if v == "2":
            print()
            return True


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def ask_email():
    """Interactive prompt shown below the banner when no --email is given."""
    while True:
        try:
            val = input("  " + C(CYAN, ">> ", True) + C(WHITE, "Enter YOUR email address: ", True)).strip()
        except EOFError:
            fail("No email entered.")
        if EMAIL_RE.match(val):
            print()
            return val
        status("x", RED, "That does not look like an email. Try again.")


def run(args):
    if args.since:
        try:
            imap_date(args.since)
        except ValueError:
            fail("--since must look like YYYY-MM-DD, e.g. 2020-01-31")

    privacy_alert()

    if args.demo:
        status("!", YELLOW, C(YELLOW, "DEMO MODE: the data below is sample data, not a real mailbox.", True))
        print_results(summarize_demo())
        footer()
        return

    if not args.email:
        args.email = ask_email()
        if sys.stdin.isatty() and not args.watch:
            args.watch = ask_mode()
    confirm_ownership(args.yes)
    boot()

    host = args.host or HOSTS.get(args.email.split("@")[-1].lower())
    if not host:
        fail("Unknown provider. Pass --host imap.yourprovider.com")

    pw = os.environ.get("MAIL_APP_PASSWORD")
    if not pw:
        status("i", CYAN, "Gmail needs a 16-character " + C(YELLOW, "APP PASSWORD", True)
               + " (not your normal password).")
        status("i", CYAN, "Create one: " + C(CYAN, "https://myaccount.google.com/apppasswords"))
        print("      " + C(GREY, "Logging in also proves the mailbox is yours."))
        pw = getpass.getpass("  App password (typing is hidden): ")
    pw = pw.replace(" ", "")

    def do_login():
        conn = imaplib.IMAP4_SSL(host)
        conn.login(args.email, pw)
        return conn

    try:
        conn = with_spinner(f"Connecting to {host} ...", do_login)
    except imaplib.IMAP4.error as e:
        msg = str(e).lower()
        if any(k in msg for k in ("application-specific", "app password",
                                  "authenticationfailed", "invalid credentials")):
            print()
            box("[!] APP PASSWORD NEEDED", [
                "Google/Yahoo/iCloud block your normal password for outside tools. "
                "This is their rule, not a bug in AccountScan.",
                "1. Open https://myaccount.google.com/security and turn ON 2-Step Verification.",
                "2. Open https://myaccount.google.com/apppasswords",
                "3. Type the name AccountScan, press Create, copy the 16 letters.",
                "4. Run AccountScan again and paste that code (spaces are fine).",
                "Your normal password was not saved anywhere.",
            ], border=YELLOW, title_color=YELLOW)
            sys.exit(1)
        fail(f"Login failed: {e}")
    except OSError as e:
        fail(f"Cannot reach {host}: {e}")
    status("+", GREEN, f"Logged in as {C(CYAN, args.email)}")

    if args.list_folders:
        list_folders(conn)
        conn.logout()
        footer()
        return

    typ, _ = conn.select(f'"{args.folder}"', readonly=True)
    if typ != "OK":
        fail(f"Cannot open folder {args.folder!r}. Use --list-folders to see the names.")
    status("+", GREEN, f"Folder opened (read-only): {C(CYAN, args.folder)}")
    if host == "imap.gmail.com" and args.folder == "INBOX":
        status("i", CYAN, 'Tip: use --folder "[Gmail]/All Mail" to search your whole mailbox.')
    print()

    if args.watch:
        watch_mode(conn, args)
        conn.logout()
        footer()
        return

    ids = find_ids(conn, args.since, args.only, lambda d, t: show_progress("Searching", d, t))
    status("+", GREEN, f"{len(ids)} matching mail(s) found")
    msgs = fetch_headers(conn, ids, on_step=lambda d, t: show_progress("Reading", d, t)) if ids else []
    conn.logout()

    rows = summarize(msgs)
    print_results(rows)
    if args.csv and rows:
        print()
        save_csv(args.csv, rows)
    footer()


def summarize_demo():
    return [{"service": d, "first": f, "last": l, "count": n, "types": t, "subject": ""}
            for d, f, l, n, t in DEMO_ROWS]


def main(argv=None):
    global COLOR, ANIM
    args = build_parser().parse_args(argv)
    setup_terminal()
    tty = sys.stdout.isatty()
    COLOR = (tty or bool(os.environ.get("FORCE_COLOR"))) and not args.no_color \
        and not os.environ.get("NO_COLOR")
    ANIM = tty and COLOR and not args.no_anim

    if not (args.demo or args.about) and not args.email and not sys.stdin.isatty():
        build_parser().error("--email is required when not running in a terminal")

    try:
        if tty:
            clear_screen()
        if not args.quick:
            matrix_intro()
        banner()
        if args.about:
            footer()
            return 0
        run(args)
    except KeyboardInterrupt:
        print()
        status("!", YELLOW, "Aborted by user.")
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
