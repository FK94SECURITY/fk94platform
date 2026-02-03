#!/usr/bin/env python3
"""
FK94 Security - X/Twitter Engagement Bot (Playwright)
Engages with cybersecurity content on X via browser automation.
No API keys needed - uses saved browser sessions.

Usage:
    python3 x_engagement.py              # Run engagement cycle
    python3 x_engagement.py --dry-run    # Preview without acting
"""

import json
import random
import sys
import time
import logging
from pathlib import Path
from datetime import datetime, date
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "x_engagement.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-x-engagement")

SESSION_DIR = Path(__file__).parent / "browser_sessions"
STATE_PATH = Path(__file__).parent / "x_engagement_state.json"

# Conservative limits to avoid bans
MAX_LIKES_PER_RUN = 5
MAX_REPLIES_PER_RUN = 3
MAX_DAILY_INTERACTIONS = 15

HASHTAGS = ["#cybersecurity", "#infosec", "#OSINT", "#datasecurity", "#privacy"]

REPLY_TEMPLATES = [
    "Great point! {topic_comment} If you want to check if your data is exposed, tools like HIBP or FK94 Security can help.",
    "This is important. {topic_comment} Everyone should regularly audit their digital footprint.",
    "Solid advice. {topic_comment} A password manager + 2FA goes a long way.",
    "{topic_comment} Security awareness is the first line of defense.",
    "Useful info! {topic_comment} Checking for breaches regularly is underrated.",
]

TOPIC_COMMENTS = {
    "password": "Password reuse is one of the biggest risks out there.",
    "breach": "Data breaches affect more people than most realize.",
    "phishing": "Phishing attacks are getting more sophisticated every day.",
    "2fa": "2FA is essential, but app-based is much better than SMS.",
    "privacy": "Digital privacy is a right, not a privilege.",
    "default": "Staying informed is key to staying safe online.",
}


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"daily_interactions": 0, "last_date": "", "replied_to": [], "liked": []}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def reset_daily_if_needed(state):
    today = date.today().isoformat()
    if state.get("last_date") != today:
        state["daily_interactions"] = 0
        state["last_date"] = today
    return state


def pick_topic_comment(text):
    text_lower = text.lower()
    for keyword, comment in TOPIC_COMMENTS.items():
        if keyword in text_lower:
            return comment
    return TOPIC_COMMENTS["default"]


def generate_reply(post_text):
    template = random.choice(REPLY_TEMPLATES)
    comment = pick_topic_comment(post_text)
    return template.format(topic_comment=comment)


def run_engagement(dry_run=False):
    state = load_state()
    state = reset_daily_if_needed(state)

    if state["daily_interactions"] >= MAX_DAILY_INTERACTIONS:
        log.info(f"Daily limit reached ({MAX_DAILY_INTERACTIONS}). Skipping.")
        return

    session_path = SESSION_DIR / "twitter_session.json"
    if not session_path.exists():
        log.error("No Twitter session found. Run: python3 browser_poster.py login twitter")
        return

    hashtag = random.choice(HASHTAGS)
    log.info(f"Searching X for: {hashtag}")

    likes_done = 0
    replies_done = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(session_path))
        page = context.new_page()

        try:
            # Navigate to search
            search_url = f"https://x.com/search?q={hashtag.replace('#', '%23')}&src=typed_query&f=live"
            page.goto(search_url, wait_until="networkidle", timeout=30000)
            time.sleep(3)

            # Scroll to load more tweets
            for _ in range(3):
                page.keyboard.press("End")
                time.sleep(2)

            # Find tweet articles
            tweets = page.locator("article[data-testid='tweet']")
            count = min(tweets.count(), 20)
            log.info(f"Found {count} tweets")

            for i in range(count):
                if likes_done >= MAX_LIKES_PER_RUN and replies_done >= MAX_REPLIES_PER_RUN:
                    break

                if state["daily_interactions"] >= MAX_DAILY_INTERACTIONS:
                    break

                try:
                    tweet = tweets.nth(i)
                    tweet_text_el = tweet.locator("div[data-testid='tweetText']")
                    if tweet_text_el.count() == 0:
                        continue

                    tweet_text = tweet_text_el.first.inner_text()

                    # Skip if already interacted
                    tweet_id = tweet_text[:50]  # Use text prefix as ID
                    if tweet_id in state.get("liked", []) or tweet_id in state.get("replied_to", []):
                        continue

                    # Like
                    if likes_done < MAX_LIKES_PER_RUN:
                        if dry_run:
                            log.info(f"[DRY RUN] Would like: {tweet_text[:80]}...")
                        else:
                            like_btn = tweet.locator("button[data-testid='like']")
                            if like_btn.count() > 0:
                                like_btn.first.click()
                                time.sleep(random.uniform(1, 3))
                                state["liked"].append(tweet_id)
                                state["daily_interactions"] += 1
                                likes_done += 1
                                log.info(f"Liked tweet: {tweet_text[:60]}...")

                    # Reply (less frequently)
                    if replies_done < MAX_REPLIES_PER_RUN and random.random() < 0.3:
                        reply_text = generate_reply(tweet_text)

                        if dry_run:
                            log.info(f"[DRY RUN] Would reply: {reply_text[:80]}...")
                        else:
                            reply_btn = tweet.locator("button[data-testid='reply']")
                            if reply_btn.count() > 0:
                                reply_btn.first.click()
                                time.sleep(2)

                                editor = page.locator("div[role='textbox'][contenteditable='true']")
                                if editor.count() > 0:
                                    editor.first.click()
                                    page.keyboard.type(reply_text, delay=15)
                                    time.sleep(1)

                                    send_btn = page.locator("button[data-testid='tweetButton']")
                                    if send_btn.count() > 0:
                                        send_btn.first.click()
                                        time.sleep(3)
                                        state["replied_to"].append(tweet_id)
                                        state["daily_interactions"] += 1
                                        replies_done += 1
                                        log.info(f"Replied to tweet: {tweet_text[:60]}...")

                    # Random delay between interactions
                    time.sleep(random.uniform(5, 15))

                except Exception as e:
                    log.warning(f"Error on tweet {i}: {e}")
                    continue

        except PlaywrightTimeout:
            log.error("Page load timeout")
        except Exception as e:
            log.error(f"Engagement error: {e}")
        finally:
            # Save session
            try:
                context.storage_state(path=str(session_path))
            except Exception:
                pass
            page.close()
            context.close()
            browser.close()

    # Keep state lists manageable
    state["liked"] = state.get("liked", [])[-200:]
    state["replied_to"] = state.get("replied_to", [])[-100:]

    save_state(state)
    log.info(f"Done. Likes: {likes_done}, Replies: {replies_done}, Daily total: {state['daily_interactions']}")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    run_engagement(dry_run=dry_run)
