#!/usr/bin/env python3
"""
FK94 Security - Social Media Auto-Poster
Runs on Raspberry Pi via cron, publishes to Twitter/X and LinkedIn.
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path

import tweepy
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "poster.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-poster")

CALENDAR_PATH = Path(__file__).parent / "content_calendar.json"
STATE_PATH = Path(__file__).parent / "poster_state.json"


def load_calendar():
    with open(CALENDAR_PATH) as f:
        return json.load(f)["posts"]


def load_state():
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_post_id": 0, "posted": []}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def validate_post(post, lang="es"):
    """Validate post content before publishing."""
    if not isinstance(post, dict):
        log.error("Invalid post: not a dict")
        return False
    if "id" not in post or not isinstance(post["id"], int):
        log.error("Invalid post: missing or bad id")
        return False
    if lang not in post or "text" not in post[lang]:
        log.error(f"Invalid post #{post.get('id')}: missing {lang} text")
        return False
    text = post[lang]["text"]
    if len(text) > 5000:
        log.error(f"Post #{post['id']} text too long ({len(text)} chars)")
        return False
    # Block suspicious content (URLs that aren't ours)
    import re
    urls = re.findall(r'https?://[^\s]+', text)
    allowed_domains = ["fk94security.com", "fk94platform.vercel.app", "haveibeenpwned.com",
                       "takeout.google.com", "facebook.com", "amazon.com"]
    for url in urls:
        if not any(domain in url for domain in allowed_domains):
            log.error(f"Post #{post['id']} contains unauthorized URL: {url}")
            return False
    return True


def get_next_post(calendar, state):
    posted_ids = set(state.get("posted", []))
    for post in calendar:
        if post["id"] not in posted_ids:
            return post
    return None


# --- Twitter/X ---

def post_twitter(text: str) -> bool:
    api_key = os.getenv("TWITTER_API_KEY")
    api_secret = os.getenv("TWITTER_API_SECRET")
    access_token = os.getenv("TWITTER_ACCESS_TOKEN")
    access_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        log.warning("Twitter credentials not configured, skipping")
        return False

    try:
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        # Twitter limit is 280 chars, truncate if needed
        if len(text) > 280:
            text = text[:277] + "..."
        response = client.create_tweet(text=text)
        log.info(f"Twitter post published: {response.data['id']}")
        return True
    except Exception as e:
        log.error(f"Twitter post failed: {e}")
        return False


# --- LinkedIn ---

def post_linkedin(text: str) -> bool:
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")

    if not access_token:
        log.warning("LinkedIn credentials not configured, skipping")
        return False

    try:
        # Get user profile ID
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

        profile_resp = requests.get(
            "https://api.linkedin.com/v2/userinfo",
            headers=headers,
        )
        profile_resp.raise_for_status()
        person_id = profile_resp.json()["sub"]

        # Create post
        post_data = {
            "author": f"urn:li:person:{person_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        post_resp = requests.post(
            "https://api.linkedin.com/v2/ugcPosts",
            headers=headers,
            json=post_data,
        )
        post_resp.raise_for_status()
        log.info(f"LinkedIn post published: {post_resp.json().get('id', 'ok')}")
        return True
    except Exception as e:
        log.error(f"LinkedIn post failed: {e}")
        return False


# --- Main ---

def main():
    lang = sys.argv[1] if len(sys.argv) > 1 else "es"

    calendar = load_calendar()
    state = load_state()
    post = get_next_post(calendar, state)

    if not post:
        log.info("All posts published! Calendar complete.")
        return

    if not validate_post(post, lang):
        log.error(f"Post #{post['id']} failed validation, skipping")
        return

    text = post[lang]["text"]
    log.info(f"Publishing post #{post['id']} ({post['type']})")

    results = {}
    for platform in post["platforms"]:
        if platform == "twitter":
            results["twitter"] = post_twitter(text)
        elif platform == "linkedin":
            results["linkedin"] = post_linkedin(text)

    if any(results.values()):
        state["last_post_id"] = post["id"]
        state["posted"].append(post["id"])
        state["last_published"] = datetime.now().isoformat()
        save_state(state)
        log.info(f"Post #{post['id']} published: {results}")
    else:
        log.warning(f"Post #{post['id']} failed on all platforms: {results}")


if __name__ == "__main__":
    main()
