#!/usr/bin/env python3
"""
FK94 Security - Content Generator (Kimi K2.5 API)
Generates social media posts from cybersecurity RSS feeds.
Uses Kimi K2.5 via OpenAI-compatible API (Moonshot, free tier).

Usage:
    python3 content_generator.py                    # Generate new batch
    python3 content_generator.py --count 10         # Generate 10 posts
    python3 content_generator.py --dry-run          # Preview without saving
"""

import json
import os
import sys
import logging
import feedparser
from pathlib import Path
from datetime import datetime
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "content_generator.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-content-generator")

CALENDAR_PATH = Path(__file__).parent / "content_calendar.json"

# Cybersecurity RSS feeds
RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://threatpost.com/feed/",
    "https://www.schneier.com/feed/atom/",
]

SYSTEM_PROMPT = """You are a cybersecurity content creator for FK94 Security, a personal security audit platform.

Create social media posts that:
1. Educate about cybersecurity threats and best practices
2. Are engaging and accessible to non-technical people
3. Include relevant hashtags (#cybersecurity #privacy #OSINT #infosec)
4. Are bilingual (Spanish and English)
5. Mix post types: tips, data facts, stories, checklists, product mentions
6. Never be spammy - prioritize genuine value
7. Keep Twitter posts under 280 characters
8. LinkedIn posts can be longer (up to 1300 chars)

FK94 Security features: email breach checking, OSINT analysis, security scoring, PDF reports, OPSEC checklist.
Website: fk94security.com

IMPORTANT: Only include URLs from these domains: fk94security.com, haveibeenpwned.com, takeout.google.com
"""

POST_TYPES = ["educativo", "tips", "dato_impactante", "producto", "historia", "checklist"]


def load_calendar():
    if CALENDAR_PATH.exists():
        with open(CALENDAR_PATH) as f:
            return json.load(f)
    return {"posts": []}


def save_calendar(calendar):
    with open(CALENDAR_PATH, "w") as f:
        json.dump(calendar, f, indent=2, ensure_ascii=False)


def fetch_news():
    """Fetch recent cybersecurity news from RSS feeds."""
    articles = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "link": entry.get("link", ""),
                    "source": feed.feed.get("title", feed_url),
                })
        except Exception as e:
            log.warning(f"Error fetching {feed_url}: {e}")
    log.info(f"Fetched {len(articles)} articles from {len(RSS_FEEDS)} feeds")
    return articles


def generate_posts(articles, count=5):
    """Generate posts using Kimi K2.5 API."""
    api_key = os.environ.get("KIMI_API_KEY") or os.environ.get("AI_API_KEY", "")
    base_url = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.ai/v1")

    if not api_key:
        log.error("No API key. Set KIMI_API_KEY or AI_API_KEY environment variable.")
        return []

    client = OpenAI(api_key=api_key, base_url=base_url)

    # Prepare news context
    news_context = "\n".join([
        f"- {a['title']} ({a['source']}): {a['summary']}"
        for a in articles[:15]
    ])

    prompt = f"""Based on these recent cybersecurity news articles, create {count} social media posts.

Recent news:
{news_context}

For each post, output JSON with this structure:
{{
  "type": "educativo|tips|dato_impactante|producto|historia|checklist",
  "platforms": ["twitter", "linkedin"],
  "es": {{"text": "Spanish version"}},
  "en": {{"text": "English version"}}
}}

Return a JSON array of {count} posts. Mix the types. Make them engaging and educational.
For "producto" type, naturally mention FK94 Security. For others, focus on pure value.
"""

    try:
        response = client.chat.completions.create(
            model=os.environ.get("AI_MODEL", "kimi-k2.5"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=4000,
        )

        content = response.choices[0].message.content

        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]

        posts = json.loads(content.strip())
        if not isinstance(posts, list):
            posts = [posts]

        log.info(f"Generated {len(posts)} posts")
        return posts

    except Exception as e:
        log.error(f"AI generation error: {e}")
        return []


def merge_posts(calendar, new_posts):
    """Add new posts to calendar with incrementing IDs and days."""
    existing = calendar.get("posts", [])
    max_id = max([p.get("id", 0) for p in existing], default=0)
    max_day = max([p.get("day", 0) for p in existing], default=0)

    for i, post in enumerate(new_posts):
        post["id"] = max_id + i + 1
        post["day"] = max_day + (i + 1) * 2  # Every 2 days
        if "platforms" not in post:
            post["platforms"] = ["twitter", "linkedin"]
        existing.append(post)

    calendar["posts"] = existing
    return calendar


def main():
    dry_run = "--dry-run" in sys.argv
    count = 5
    for i, arg in enumerate(sys.argv):
        if arg == "--count" and i + 1 < len(sys.argv):
            count = int(sys.argv[i + 1])

    log.info(f"Generating {count} posts (dry_run={dry_run})")

    # Fetch news
    articles = fetch_news()
    if not articles:
        log.warning("No articles fetched. Using generic generation.")

    # Generate posts
    new_posts = generate_posts(articles, count=count)
    if not new_posts:
        log.error("No posts generated")
        return

    if dry_run:
        for post in new_posts:
            log.info(f"[DRY RUN] {post.get('type', 'unknown')}: {post.get('es', {}).get('text', '')[:80]}...")
        return

    # Merge into calendar
    calendar = load_calendar()
    calendar = merge_posts(calendar, new_posts)
    save_calendar(calendar)
    log.info(f"Calendar now has {len(calendar['posts'])} total posts")


if __name__ == "__main__":
    main()
