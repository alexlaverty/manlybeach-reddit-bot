import os
import csv
import tweepy
import praw

TWEET_CSV = "shark_tweets.csv"
SUBREDDIT_NAME = "aleximinal"
SHARKSMART_USERNAME = "NSWSharkSmart"
SEARCH_TERM = "manly beach"

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


def get_twitter_client():
    """Create and return a Tweepy client using a bearer token."""
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise ValueError("TWITTER_BEARER_TOKEN environment variable is not set")
    return tweepy.Client(bearer_token=bearer_token)


def get_reddit_client():
    """Create and return a PRAW Reddit instance."""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
    )


def fetch_shark_tweets(client):
    """Fetch recent tweets from @NSWSharkSmart that mention 'manly beach'."""
    # Look up the user ID for @NSWSharkSmart
    user = client.get_user(username=SHARKSMART_USERNAME)
    if not user.data:
        print(f"Could not find user @{SHARKSMART_USERNAME}")
        return []

    user_id = user.data.id

    # Fetch recent tweets from the user's timeline
    tweets = client.get_users_tweets(
        user_id,
        max_results=100,
        tweet_fields=["id", "text", "created_at"],
    )

    if not tweets.data:
        print(f"No recent tweets found for @{SHARKSMART_USERNAME}")
        return []

    # Filter for tweets that mention "manly beach" (case insensitive)
    matching = [t for t in tweets.data if SEARCH_TERM in t.text.lower()]
    print(f"Found {len(matching)} tweet(s) mentioning '{SEARCH_TERM}'")
    return matching


def post_tweet_to_reddit(reddit, tweet):
    """Post a tweet as a self-text post to the subreddit."""
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    tweet_url = f"https://x.com/{SHARKSMART_USERNAME}/status/{tweet.id}"

    # Use the first ~80 chars of the tweet as the title
    title = tweet.text[:80]
    if len(tweet.text) > 80:
        title = title.rsplit(" ", 1)[0] + "..."

    body = f"{tweet.text}\n\n[Source]({tweet_url})"

    try:
        subreddit.submit(title, selftext=body)
        print(f"Posted tweet {tweet.id} to r/{SUBREDDIT_NAME}")
        return True
    except Exception as e:
        print(f"Error posting tweet {tweet.id} to r/{SUBREDDIT_NAME}: {e}")
        return False


def main():
    posted_ids = get_posted_tweet_ids()
    print(f"Loaded {len(posted_ids)} previously posted tweet ID(s)")

    twitter = get_twitter_client()
    reddit = get_reddit_client()

    tweets = fetch_shark_tweets(twitter)

    new_count = 0
    for tweet in tweets:
        tweet_id = str(tweet.id)
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
