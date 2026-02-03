#!/usr/bin/env python3
"""
FK94 Security - Browser-based Social Media Poster
Uses Playwright to publish posts via real browser on Raspberry Pi.
No API keys needed - uses saved browser sessions.
"""

import json
import sys
import time
import logging
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(Path(__file__).parent / "browser_poster.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("fk94-browser-poster")

CALENDAR_PATH = Path(__file__).parent / "content_calendar.json"
STATE_PATH = Path(__file__).parent / "poster_state.json"
SESSION_DIR = Path(__file__).parent / "browser_sessions"


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
    import re
    if not isinstance(post, dict) or "id" not in post:
        return False
    if lang not in post or "text" not in post[lang]:
        return False
    text = post[lang]["text"]
    if len(text) > 5000:
        log.error(f"Post #{post['id']} text too long")
        return False
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


# --- LinkedIn ---

def login_linkedin(page, email: str, password: str):
    """Login to LinkedIn. Only needed once - session is saved."""
    page.goto("https://www.linkedin.com/login")
    page.fill("#username", email)
    page.fill("#password", password)
    page.click("button[type='submit']")
    page.wait_for_url("**/feed/**", timeout=30000)
    log.info("LinkedIn login successful")


def post_linkedin(context, text: str) -> bool:
    """Post to LinkedIn using browser."""
    try:
        page = context.new_page()
        page.goto("https://www.linkedin.com/feed/", wait_until="networkidle", timeout=30000)
        time.sleep(3)

        # Click "Start a post" button
        start_post = page.locator("button.share-box-feed-entry__trigger, button[class*='artdeco-button'][class*='share-box']")
        if start_post.count() == 0:
            # Try alternative selector
            start_post = page.locator("text=Start a post")
        start_post.first.click()
        time.sleep(2)

        # Type in the post editor
        editor = page.locator("div.ql-editor[contenteditable='true'], div[role='textbox'][contenteditable='true']")
        editor.first.click()

        # Type the text line by line to preserve formatting
        for i, line in enumerate(text.split("\n")):
            if i > 0:
                page.keyboard.press("Enter")
            if line.strip():
                page.keyboard.type(line, delay=10)

        time.sleep(1)

        # Click Post button
        post_btn = page.locator("button.share-actions__primary-action, button:has-text('Post')")
        post_btn.first.click()
        time.sleep(3)

        log.info("LinkedIn post published successfully")
        page.close()
        return True

    except Exception as e:
        log.error(f"LinkedIn post failed: {e}")
        try:
            page.close()
        except:
            pass
        return False


# --- Twitter/X ---

def login_twitter(page, username: str, password: str):
    """Login to Twitter/X. Only needed once - session is saved."""
    page.goto("https://x.com/i/flow/login")
    time.sleep(3)

    # Enter username
    username_input = page.locator("input[autocomplete='username']")
    username_input.fill(username)
    page.locator("text=Next").click()
    time.sleep(2)

    # Enter password
    password_input = page.locator("input[type='password']")
    password_input.fill(password)
    page.locator("text=Log in").click()
    page.wait_for_url("**/home", timeout=30000)
    log.info("Twitter login successful")


def post_twitter(context, text: str) -> bool:
    """Post to Twitter/X using browser."""
    try:
        page = context.new_page()
        page.goto("https://x.com/compose/post", wait_until="networkidle", timeout=30000)
        time.sleep(3)

        # Type in compose box
        editor = page.locator("div[role='textbox'][contenteditable='true']")
        editor.first.click()

        # Twitter has 280 char limit
        if len(text) > 280:
            text = text[:277] + "..."

        page.keyboard.type(text, delay=10)
        time.sleep(1)

        # Click Post button
        post_btn = page.locator("button[data-testid='tweetButton']")
        post_btn.click()
        time.sleep(3)

        log.info("Twitter post published successfully")
        page.close()
        return True

    except Exception as e:
        log.error(f"Twitter post failed: {e}")
        try:
            page.close()
        except:
            pass
        return False


# --- Reddit ---

def login_reddit(page, username: str, password: str):
    """Login to Reddit. Only needed once - session is saved."""
    page.goto("https://www.reddit.com/login/")
    time.sleep(3)

    username_input = page.locator("input[name='username'], input#loginUsername")
    if username_input.count() > 0:
        username_input.first.fill(username)

    password_input = page.locator("input[name='password'], input#loginPassword")
    if password_input.count() > 0:
        password_input.first.fill(password)

    login_btn = page.locator("button[type='submit']:has-text('Log In'), button:has-text('Log In')")
    if login_btn.count() > 0:
        login_btn.first.click()

    page.wait_for_url("**/reddit.com/**", timeout=30000)
    time.sleep(3)
    log.info("Reddit login successful")


def post_reddit(context, text: str, subreddit: str = "cybersecurity") -> bool:
    """Post to Reddit using browser."""
    try:
        page = context.new_page()
        page.goto(f"https://www.reddit.com/r/{subreddit}/submit", wait_until="networkidle", timeout=30000)
        time.sleep(3)

        # Select "Text" post tab
        text_tab = page.locator("button:has-text('Text'), a:has-text('Text')")
        if text_tab.count() > 0:
            text_tab.first.click()
            time.sleep(1)

        # Title (first line or first 100 chars)
        lines = text.split("\n")
        title = lines[0][:100] if lines else text[:100]
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        title_input = page.locator("textarea[placeholder*='Title'], input[placeholder*='Title']")
        if title_input.count() > 0:
            title_input.first.fill(title)
            time.sleep(1)

        # Body
        if body:
            body_input = page.locator("div[contenteditable='true'], textarea[placeholder*='Text']")
            if body_input.count() > 0:
                body_input.first.click()
                page.keyboard.type(body, delay=10)
                time.sleep(1)

        # Submit
        submit_btn = page.locator("button:has-text('Post'), button[type='submit']:has-text('Post')")
        if submit_btn.count() > 0:
            submit_btn.first.click()
            time.sleep(5)

        log.info("Reddit post published successfully")
        page.close()
        return True

    except Exception as e:
        log.error(f"Reddit post failed: {e}")
        try:
            page.close()
        except:
            pass
        return False


# --- Main ---

def setup_login(platform: str, email: str, password: str):
    """One-time login to save session cookies."""
    SESSION_DIR.mkdir(exist_ok=True)
    storage_path = SESSION_DIR / f"{platform}_session.json"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        if platform == "linkedin":
            login_linkedin(page, email, password)
        elif platform == "twitter":
            login_twitter(page, email, password)
        elif platform == "reddit":
            login_reddit(page, email, password)
        else:
            log.error(f"Unknown platform: {platform}")
            browser.close()
            return

        # Save session
        context.storage_state(path=str(storage_path))
        log.info(f"Session saved to {storage_path}")
        browser.close()


def publish(platforms=None, lang="es"):
    """Publish next post from calendar."""
    calendar = load_calendar()
    state = load_state()
    post = get_next_post(calendar, state)

    if not post:
        log.info("All posts published! Calendar complete.")
        return None

    if not validate_post(post, lang):
        log.error(f"Post #{post['id']} failed validation, skipping")
        return None

    text = post[lang]["text"]
    target_platforms = platforms or post.get("platforms", ["linkedin", "twitter"])

    log.info(f"Publishing post #{post['id']} ({post['type']}) to {target_platforms}")

    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for platform in target_platforms:
            storage_path = SESSION_DIR / f"{platform}_session.json"
            if not storage_path.exists():
                log.warning(f"No session for {platform}. Run: python3 browser_poster.py login {platform}")
                results[platform] = False
                continue

            context = browser.new_context(storage_state=str(storage_path))

            if platform == "linkedin":
                results["linkedin"] = post_linkedin(context, text)
            elif platform == "twitter":
                tweet_text = text if len(text) <= 280 else text[:277] + "..."
                results["twitter"] = post_twitter(context, tweet_text)
            elif platform == "reddit":
                results["reddit"] = post_reddit(context, text)

            # Update saved session
            context.storage_state(path=str(storage_path))
            context.close()

        browser.close()

    if any(results.values()):
        state["last_post_id"] = post["id"]
        state["posted"].append(post["id"])
        from datetime import datetime
        state["last_published"] = datetime.now().isoformat()
        state["last_results"] = results
        save_state(state)
        log.info(f"Post #{post['id']} done: {results}")
    else:
        log.warning(f"Post #{post['id']} failed on all platforms")

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 browser_poster.py login linkedin   # One-time login (needs monitor)")
        print("  python3 browser_poster.py login twitter    # One-time login (needs monitor)")
        print("  python3 browser_poster.py login reddit     # One-time login (needs monitor)")
        print("  python3 browser_poster.py post             # Publish next post (all platforms)")
        print("  python3 browser_poster.py post twitter     # Publish only to Twitter")
        print("  python3 browser_poster.py post linkedin    # Publish only to LinkedIn")
        print("  python3 browser_poster.py post reddit      # Publish only to Reddit")
        print("  python3 browser_poster.py status           # Show calendar status")
        print("  python3 browser_poster.py --setup          # Interactive setup for all platforms")
        return

    cmd = sys.argv[1]

    if cmd == "login":
        platform = sys.argv[2] if len(sys.argv) > 2 else "linkedin"
        email = input(f"Enter {platform} email/username: ")
        password = input(f"Enter {platform} password: ")
        setup_login(platform, email, password)

    elif cmd == "post":
        platforms = [sys.argv[2]] if len(sys.argv) > 2 else None
        results = publish(platforms=platforms)
        if results:
            print(f"Results: {results}")

    elif cmd == "status":
        calendar = load_calendar()
        state = load_state()
        posted = set(state.get("posted", []))
        total = len(calendar)
        done = len(posted)
        print(f"Calendar: {done}/{total} posts published")
        print(f"Last published: {state.get('last_published', 'never')}")
        next_post = get_next_post(calendar, state)
        if next_post:
            print(f"Next: #{next_post['id']} - {next_post['type']}")
        # Show session status
        for platform in ["twitter", "linkedin", "reddit"]:
            sp = SESSION_DIR / f"{platform}_session.json"
            status = "ready" if sp.exists() else "not logged in"
            print(f"  {platform}: {status}")

    elif cmd == "--setup":
        for platform in ["twitter", "linkedin", "reddit"]:
            print(f"\n--- {platform.upper()} ---")
            answer = input(f"Setup {platform}? (y/n): ").strip().lower()
            if answer == "y":
                email = input(f"  {platform} username/email: ")
                password = input(f"  {platform} password: ")
                setup_login(platform, email, password)


if __name__ == "__main__":
    main()
