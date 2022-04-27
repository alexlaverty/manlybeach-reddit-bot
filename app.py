import requests
import urllib.request

import pandas as pd
import os
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import yaml
import praw
from random import randint

# Websites to add :

parser = argparse.ArgumentParser()
parser.add_argument('--local',  help='Pull html from local file', action='store_true')
args = parser.parse_args()

csv_file = "data.csv"

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)
pd.set_option('max_colwidth', -1)

# def print_full(x):
#     pd.set_option('display.max_rows', len(x))
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.width', 2000)
#     pd.set_option('display.float_format', '{:20,.2f}'.format)
#     pd.set_option('display.max_colwidth', -1)
#     print(x)
#     pd.reset_option('display.max_rows')
#     pd.reset_option('display.max_columns')
#     pd.reset_option('display.width')
#     pd.reset_option('display.float_format')
#     pd.reset_option('display.max_colwidth')

def initialise_csv():
    csv_exists = os.path.isfile(csv_file)
    if not csv_exists:
        new_csv = pd.DataFrame(columns=["timestamp","title", "url","posted"])
        new_csv.to_csv(csv_file, index=False)

def ninenews():
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        # Get Remote
        remote_url = 'https://www.9news.com.au/manly'
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find_all('h1', {'class' : 'story__headline'})

    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    for headline in headlines:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title=headline.find('span', {'class' : 'story__headline__text'}).text
        try:

            url = headline.find('a')['href']
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass
    print(remote_url)
    print(df)
    print("==================================")
    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)

def manlyaustralia():
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        # Get Remote
        remote_url = 'https://www.manlyaustralia.com.au/news/'
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find_all('div', {'class' : 'desc'})

    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    for headline in headlines:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title="{} :: {}".format(headline.find('a').contents[0],"Manly Australia")
        try:
            url = headline.find('a')['href']
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass

    print(remote_url)
    print(df)
    print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)


def manlyobserver():
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        # Get Remote
        remote_url = 'https://manlyobserver.com.au/category/latest-news/'
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find_all('div', {'class' : 'td-module-thumb'})
    #print(headlines)

    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    for headline in headlines:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url_text = headline.find('a')['title']
        title="{} :: {}".format(url_text,"Manly Observer")
        try:
            url = headline.find('a')['href']
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass

    print(remote_url)
    print(df)
    print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)


def northernbeachesadvocate():
    url_name = "Northern Beaches Advocate"
    remote_url = 'https://www.northernbeachesadvocate.com.au/?s=manly'
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        page = urllib.request.urlopen(remote_url)

        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find_all('article')
    print(headlines)

    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    for headline in headlines:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        url_text = headline.find('a')['title']
        title="{} :: {}".format(url_text, url_name)
        try:
            url = headline.find('a')['href']
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass

    print(remote_url)
    print(df)
    print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)


def sproutdaily():
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        # Get Remote
        remote_url = 'https://www.sproutdaily.com'
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find_all('div', {'class' : 'summary-title'})

    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    for headline in headlines:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title="{} :: {}".format(headline.find('a').contents[0], "Sprout Daily")
        try:
            url = "{}{}".format(remote_url, headline.find('a')['href'])
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass

    print(remote_url)
    print(df)
    print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)


def pacificjules():
    remote_url = 'https://pacificjules.typepad.com/'
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')

    rows = []

    headlines = soup.find('div', {'class' : 'module-archives'})
    lis = headlines.find_all('li', {'class' : 'module-list-item'})
    csv = pd.read_csv(csv_file)

    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])
    for li in lis:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        title="{} :: {}".format(li.find('a').contents[0],"Bold and Beautiful")
        try:
            url = li.find('a')['href']
            #print(title, url)
            df = df.append({
                 "timestamp": timestamp,
                 "title": title,
                 "url": url,
                 "posted": "False",
            }, ignore_index=True)
        except TypeError:
            pass

    print(remote_url)
    print(df)
    print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['url'],inplace=True)
    csv.to_csv(csv_file, index=False)


def publish_to_reddit():
    # with open("config.yml", 'r') as ymlfile:
    #     cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    # username      = cfg['reddit']['username']
    # password      = cfg['reddit']['password']
    # sub_reddit    = cfg['reddit']['sub_reddit']
    # client_id     = cfg['reddit']['client_id']
    # client_secret = cfg['reddit']['client_secret']
    # user_agent    = cfg['reddit']['user_agent']

    username      = os.getenv('REDDIT_USERNAME')
    password      = os.getenv('REDDIT_PASSWORD')
    sub_reddit    = os.getenv('REDDIT_SUB_REDDIT')
    client_id     = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    user_agent    = os.getenv('REDDIT_USER_AGENT')

    csv = pd.read_csv(csv_file)
    print("Publishing to Subreddit : {}".format(sub_reddit))

    print("==================================")

    reddit = praw.Reddit(username=username,
                         password=password,
                         client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent
                         )

    for index, row in csv.iterrows():
        if row['posted'] == False:
            title=row['title']
            url=row['url']
            print("Title : {}".format(title))
            print("URL : {}".format(url))
            wait_for=randint(600, 900)
            try:
                reddit.subreddit(sub_reddit).submit(title, url=url)
                print("POSTED TO REDDIT!")
                csv.at[index,'posted'] = "True"
                csv.to_csv(csv_file, index=False)
                print("Waiting for random ammount of seconds before posting again : {}".format(str(wait_for)))
                sleep(wait_for)
            except TypeError as error:
                print(error)
                pass
            print("----------------------------------")

def main():
    initialise_csv()
    ninenews()
    manlyaustralia()
    sproutdaily()
    pacificjules()
    manlyobserver()
    northernbeachesadvocate()
    publish_to_reddit()

if __name__ == '__main__':
    main()
