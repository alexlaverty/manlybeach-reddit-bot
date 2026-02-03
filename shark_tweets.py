import os
import csv
import re
import json
import requests
import praw

TWEET_CSV = "shark_tweets.csv"
SUBREDDIT_NAME = "aleximinal"
SHARKSMART_USERNAME = "NSWSharkSmart"
SEARCH_TERM = "manly beach"
SYNDICATION_URL = (
    "https://syndication.twitter.com/srv/timeline-profile/screen-name/"
    + SHARKSMART_USERNAME
)

# Post SharkSmart Tweets mentioning "manly beach" to Reddit


def get_posted_tweet_ids():
    """Read previously posted tweet IDs from the CSV file."""
    tweet_ids = set()
    if os.path.exists(TWEET_CSV):
        with open(TWEET_CSV, "r") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if row:
                    tweet_ids.add(row[0])
    return tweet_ids


def save_tweet_id(tweet_id):
    """Append a tweet ID to the CSV file."""
    file_exists = os.path.exists(TWEET_CSV)
    with open(TWEET_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["tweet_id"])
        writer.writerow([tweet_id])


def get_reddit_client():
    """Create and return a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )


def fetch_shark_tweets():
    """Fetch recent tweets from @NSWSharkSmart via the syndication endpoint."""
    response = requests.get(SYNDICATION_URL)
    response.raise_for_status()

    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    if not match:
        print("Could not find tweet data in syndication response")
        return []

    data = json.loads(match.group(1))
    entries = data["props"]["pageProps"]["timeline"]["entries"]

    tweets = []
    for entry in entries:
        if entry.get("type") == "tweet":
            tweet = entry["content"]["tweet"]
            tweets.append(tweet)

    print(f"Fetched {len(tweets)} tweet(s) from @{SHARKSMART_USERNAME}")

    # Filter for tweets that mention "manly beach" (case insensitive)
    matching = [t for t in tweets if SEARCH_TERM in t["full_text"].lower()]
    print(f"Found {len(matching)} tweet(s) mentioning '{SEARCH_TERM}'")
    return matching


def post_tweet_to_reddit(reddit, tweet):
    """Post a tweet as a self-text post to the subreddit."""
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    tweet_url = f"https://x.com/{SHARKSMART_USERNAME}/status/{tweet['id_str']}"

    # Use the first ~80 chars of the tweet as the title
    text = tweet["full_text"]
    title = text[:80]
    if len(text) > 80:
        title = title.rsplit(" ", 1)[0] + "..."

    body = f"{text}\n\n[Source]({tweet_url})"

    try:
        subreddit.submit(title, selftext=body)
        print(f"Posted tweet {tweet['id_str']} to r/{SUBREDDIT_NAME}")
        return True
    except Exception as e:
        print(f"Error posting tweet {tweet['id_str']} to r/{SUBREDDIT_NAME}: {e}")
        return False


def main():
    posted_ids = get_posted_tweet_ids()
    print(f"Loaded {len(posted_ids)} previously posted tweet ID(s)")

    tweets = fetch_shark_tweets()
    reddit = get_reddit_client()

    new_count = 0
    for tweet in tweets:
        tweet_id = tweet["id_str"]
        if tweet_id in posted_ids:
            print(f"Skipping already posted tweet {tweet_id}")
            continue

        if post_tweet_to_reddit(reddit, tweet):
            save_tweet_id(tweet_id)
            posted_ids.add(tweet_id)
            new_count += 1

    print(f"Done. Posted {new_count} new tweet(s) to r/{SUBREDDIT_NAME}")


if __name__ == "__main__":
    main()
