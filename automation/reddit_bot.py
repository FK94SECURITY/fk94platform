#!/usr/bin/env python3
"""
FK94 Security - Reddit Engagement Bot (Playwright)
Participates in cybersecurity subreddits via browser automation.
No API keys needed - uses saved browser sessions.

Usage:
    python3 reddit_bot.py              # Run engagement cycle
    python3 reddit_bot.py --dry-run    # Preview without acting
"""

import json
import random
import sys
import time
import logging
from pathlib import Path
from datetime import date
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "reddit_bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-reddit-bot")

SESSION_DIR = Path(__file__).parent / "browser_sessions"
STATE_PATH = Path(__file__).parent / "reddit_state.json"

MAX_REPLIES_PER_RUN = 2
MAX_DAILY_REPLIES = 3

SUBREDDITS = [
    "cybersecurity",
    "privacy",
    "netsec",
    "AskNetsec",
    "hacking",
    "InfoSecNews",
]

# Helpful responses (NOT spammy - genuine value)
RESPONSE_TEMPLATES = {
    "breach": [
        "You can check if your email was in this breach (or any other) at haveibeenpwned.com. "
        "It's free and maintained by Troy Hunt. If you find hits, change those passwords immediately "
        "and enable 2FA wherever possible.",
        "After any major breach, the priority list is: 1) Change passwords for affected accounts, "
        "2) Enable 2FA (app-based, not SMS), 3) Check haveibeenpwned.com for your email, "
        "4) Monitor your accounts for unusual activity.",
    ],
    "password": [
        "A good password strategy: use a password manager (Bitwarden is free and open-source), "
        "generate unique 16+ character passwords for everything, and use app-based 2FA. "
        "The days of remembering passwords should be over.",
        "If you're looking for a solid setup: Bitwarden for passwords, Authy or Aegis for 2FA, "
        "and a hardware key (YubiKey) for your most important accounts. That covers 99% of threats.",
    ],
    "privacy": [
        "Good privacy hygiene: use email aliases for signups (SimpleLogin or Firefox Relay), "
        "a privacy-focused browser (Firefox or Brave), and check what data companies have on you. "
        "Google Takeout and Facebook's Download Your Information are eye-opening.",
        "For privacy, compartmentalization is key. Different emails for different purposes: "
        "one for banking/important stuff, one for social media, one for random signups. "
        "A password manager makes this manageable.",
    ],
    "general": [
        "The basics still matter more than anything: unique passwords everywhere, "
        "2FA on all important accounts, keep software updated, and be skeptical of unsolicited "
        "messages. These four things prevent the vast majority of attacks.",
        "Security is a spectrum, not a destination. Start with the basics (password manager + 2FA), "
        "then gradually improve. Trying to do everything at once leads to burnout and giving up.",
    ],
}

# Keywords to match response category
KEYWORDS = {
    "breach": ["breach", "leaked", "pwned", "hack", "compromised", "data leak", "exposed"],
    "password": ["password", "credential", "passkey", "authentication", "login"],
    "privacy": ["privacy", "tracking", "surveillance", "data collection", "fingerprint"],
}


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"daily_replies": 0, "last_date": "", "replied_to": []}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def reset_daily_if_needed(state):
    today = date.today().isoformat()
    if state.get("last_date") != today:
        state["daily_replies"] = 0
        state["last_date"] = today
    return state


def categorize_post(title, body=""):
    text = (title + " " + body).lower()
    for category, words in KEYWORDS.items():
        if any(w in text for w in words):
            return category
    return "general"


def pick_response(category):
    templates = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["general"])
    return random.choice(templates)


def run_engagement(dry_run=False):
    state = load_state()
    state = reset_daily_if_needed(state)

    if state["daily_replies"] >= MAX_DAILY_REPLIES:
        log.info(f"Daily limit reached ({MAX_DAILY_REPLIES}). Skipping.")
        return

    session_path = SESSION_DIR / "reddit_session.json"
    if not session_path.exists():
        log.error("No Reddit session found. Run: python3 browser_poster.py login reddit")
        return

    subreddit = random.choice(SUBREDDITS)
    log.info(f"Browsing r/{subreddit}")

    replies_done = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(session_path))
        page = context.new_page()

        try:
            # Navigate to subreddit (new posts)
            page.goto(f"https://www.reddit.com/r/{subreddit}/new/", wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Find post links
            posts = page.locator("a[data-testid='post-title'], shreddit-post")
            count = min(posts.count(), 15)
            log.info(f"Found {count} posts in r/{subreddit}")

            post_data = []
            for i in range(count):
                try:
                    post = posts.nth(i)
                    title = post.inner_text().strip()
                    href = post.get_attribute("href")
                    if title and href and title[:40] not in state.get("replied_to", []):
                        post_data.append({"title": title, "href": href, "id": title[:40]})
                except Exception:
                    continue

            # Visit and reply to relevant posts
            for post_info in post_data:
                if replies_done >= MAX_REPLIES_PER_RUN:
                    break
                if state["daily_replies"] >= MAX_DAILY_REPLIES:
                    break

                category = categorize_post(post_info["title"])
                # Only reply to posts we can add value to
                if category == "general" and random.random() < 0.7:
                    continue

                response = pick_response(category)

                if dry_run:
                    log.info(f"[DRY RUN] Would reply to: {post_info['title'][:60]}...")
                    log.info(f"[DRY RUN] Response: {response[:80]}...")
                    replies_done += 1
                    continue

                try:
                    url = post_info["href"]
                    if not url.startswith("http"):
                        url = f"https://www.reddit.com{url}"

                    page.goto(url, wait_until="networkidle", timeout=30000)
                    time.sleep(3)

                    # Find comment box
                    comment_box = page.locator("div[contenteditable='true'][role='textbox']")
                    if comment_box.count() == 0:
                        # Try the shreddit comment box
                        comment_box = page.locator("shreddit-composer div[contenteditable='true']")

                    if comment_box.count() > 0:
                        comment_box.first.click()
                        time.sleep(1)
                        page.keyboard.type(response, delay=10)
                        time.sleep(1)

                        # Click submit
                        submit_btn = page.locator("button:has-text('Comment'), button[type='submit']:has-text('Comment')")
                        if submit_btn.count() > 0:
                            submit_btn.first.click()
                            time.sleep(3)

                            state["replied_to"].append(post_info["id"])
                            state["daily_replies"] += 1
                            replies_done += 1
                            log.info(f"Replied to: {post_info['title'][:60]}...")

                    # Random delay
                    time.sleep(random.uniform(30, 90))

                except Exception as e:
                    log.warning(f"Error replying to post: {e}")
                    continue

        except PlaywrightTimeout:
            log.error("Page load timeout")
        except Exception as e:
            log.error(f"Reddit engagement error: {e}")
        finally:
            try:
                context.storage_state(path=str(session_path))
            except Exception:
                pass
            page.close()
            context.close()
            browser.close()

    # Keep state list manageable
    state["replied_to"] = state.get("replied_to", [])[-200:]
    save_state(state)
    log.info(f"Done. Replies: {replies_done}, Daily total: {state['daily_replies']}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run_engagement(dry_run=dry_run)
