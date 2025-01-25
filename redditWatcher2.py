import os
import time
from datetime import datetime, timedelta
import praw
import smtplib
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Environment variables loaded")

required_vars = [
    'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET',
    'EMAIL_FROM', 'EMAIL_TO', 'EMAIL_USERNAME', 'EMAIL_PASSWORD'
]

for var in required_vars:
    if not os.getenv(var):
        logger.error(f"Missing required environment variable: {var}")
    else:
        logger.debug(f"Found {var}: {os.getenv(var)[:3]}{'*' * 10}")

try:
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent='SwapMonitor/1.0'
    )
    logger.info("Reddit API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Reddit API: {e}")
    raise


def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = os.getenv('EMAIL_FROM')
        msg['To'] = os.getenv('EMAIL_TO')

        logger.debug(f"Attempting to send email from {
                     msg['From']} to {msg['To']}")

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            logger.debug("Connected to SMTP server")
            smtp_server.set_debuglevel(1)

            logger.debug(f"Attempting login with username: {
                         os.getenv('EMAIL_USERNAME')}")
            smtp_server.login(os.getenv('EMAIL_USERNAME'),
                              os.getenv('EMAIL_PASSWORD'))
            logger.debug("SMTP login successful")

            smtp_server.sendmail(msg['From'], msg['To'], msg.as_string())
            logger.info("Email sent successfully")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed: {e}")
        logger.error("Please verify your email credentials and app password")
        raise
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


def send_notification(title, url):
    logger.info(f"Sending notification for post: {title}")
    send_email(
        "New iPad Listing Alert",
        f"Title: {title}\nURL: {url}"
    )


class PostCache:
    def __init__(self, max_age_minutes=60):
        self.cache = {}  # {post_id: timestamp}
        self.max_age = timedelta(minutes=max_age_minutes)

    def add(self, post_id):
        self.cache[post_id] = datetime.now()
        self._cleanup()

    def __contains__(self, post_id):
        return post_id in self.cache

    def _cleanup(self):
        current_time = datetime.now()
        self.cache = {
            post_id: timestamp
            for post_id, timestamp in self.cache.items()
            if current_time - timestamp <= self.max_age
        }
        logger.debug(f"Cache size after cleanup: {len(self.cache)}")


def check_subreddit(subreddit_name, post_cache):
    logger.info(f"Checking subreddit: {subreddit_name}")
    try:
        subreddit = reddit.subreddit(subreddit_name)
        for post in subreddit.new(limit=10):
            title_lower = post.title.lower()
            if ("ipad" in title_lower or "ipad pro" in title_lower) and post.id not in post_cache:
                logger.info(f"Found new matching post: {post.title}")
                send_notification(post.title, post.url)
                post_cache.add(post.id)
    except Exception as e:
        logger.error(f"Error checking subreddit {subreddit_name}: {e}")
        raise


def main():
    logger.info("Starting Reddit monitor")
    post_cache = PostCache()

    while True:
        try:
            for subreddit in ['appleswap', 'hardwareswap']:
                check_subreddit(subreddit, post_cache)
            logger.debug("Waiting 5 minutes before next check")
            time.sleep(300)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            logger.info("Waiting 60 seconds before retry")
            time.sleep(60)


if __name__ == "__main__":
    main()
