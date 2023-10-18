import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from random import randint
from time import sleep
import praw
from datetime import datetime

csv_file = "data.csv"

# Your Reddit API credentials
username = os.getenv('REDDIT_USERNAME')
password = os.getenv('REDDIT_PASSWORD')
sub_reddit = os.getenv('REDDIT_SUB_REDDIT')
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = os.getenv('REDDIT_USER_AGENT')

# Set up the Reddit API
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    username=username,
    password=password,
    user_agent=user_agent,
)

# Define the websites and their selectors
websites = [
    {
        "url": "https://www.sproutdaily.com/the-daily",
        "title_selector": '.BlogList-item-title',
        "url_selector": '.BlogList-item-title',
    },
    {
        "url": "https://manlyobserver.com.au/category/latest-news",
        "title_selector": 'h3',
        "url_selector": 'h3 a',
    },
    {
        "url": "https://www.9news.com.au/manly",
        "title_selector": 'span.story__headline__text',
        "url_selector": 'h3.story__headline a.story__headline__link',
    },
    {
        "url": "https://www.northernbeachesadvocate.com.au/?s=manly",
        "title_selector": 'h2.post-title.entry-title a',
        "url_selector": 'h2.post-title.entry-title a',
    },
]


def scrape_articles(url, title_selector, url_selector):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        article_titles = [element.text for element in
                          soup.select(title_selector)]

        article_urls = [urljoin(url, element['href']) for element in
                        soup.select(url_selector)]

        return list(zip(article_titles, article_urls))

    except Exception as e:
        print(f"Error: {e}")
        return []


def write_to_csv(data):
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.DataFrame(data, columns=["title", "url"])
    df.insert(0, "timestamp", current_date)
    df["posted"] = False
    df.to_csv(csv_file,
              mode="a",
              header=not os.path.exists(csv_file),
              index=False)





# Function to post articles to the subreddit
def post_to_subreddit(title, url):
    subreddit_name = "manlybeach"
    subreddit = reddit.subreddit(subreddit_name)

    try:
        subreddit.submit(title, url=url)
        print(f"Posted '{title}' to r/{subreddit_name}.")
        return True
    except Exception as e:
        print(f"Error posting '{title}' to r/{subreddit_name}: {e}")
        return False


for website in websites:
    url = website["url"]
    title_selector = website["title_selector"]
    url_selector = website["url_selector"]

    article_data = scrape_articles(url, title_selector, url_selector)

    print(f"Scraping from {url}:")
    for title, url in article_data:
        print("Title:", title)
        print("URL:", url)
        print("======================================")

    # Write the scraped data to the CSV file
    write_to_csv(article_data)


# Read the CSV file and filter rows where "Posted" is False
df = pd.read_csv(csv_file)

for index, row in df.iterrows():
    if not row["posted"]:
        title = row["title"]
        url = row["url"]
        if post_to_subreddit(title, url):
            # Update the "Posted" column to True for the posted articles
            df.at[index, "posted"] = True
            wait_for = randint(600, 900)
            print(f"Sleeping for {str(wait_for)} seconds...")
            sleep(wait_for)

# Save the updated DataFrame with "Posted" values back to the CSV file
df.to_csv(csv_file, index=False)
