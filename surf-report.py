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
from markdownify import markdownify as md

# Websites to add :

parser = argparse.ArgumentParser()
parser.add_argument('--local',  help='Pull html from local file', action='store_true')
args = parser.parse_args()

csv_file = "data-surf-report.csv"

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000)
    pd.set_option('display.float_format', '{:20,.2f}'.format)
    pd.set_option('display.max_colwidth', -1)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    pd.reset_option('display.float_format')
    pd.reset_option('display.max_colwidth')

def initialise_csv():
    csv_exists = os.path.isfile(csv_file)
    if not csv_exists:
        new_csv = pd.DataFrame(columns=["timestamp","title", "url","posted"])
        new_csv.to_csv(csv_file, index=False)



def surfreport():
    remote_url = 'https://www.swellnet.com/reports/australia/new-south-wales/northern-beaches'
    if args.local:
        soup = BeautifulSoup(open("index.html"), "html.parser")
    else:
        page = urllib.request.urlopen(remote_url)
        soup = BeautifulSoup(page, 'html.parser')
    csv = pd.read_csv(csv_file)
    rows = []

    headlines = soup.find('div', {'class' : 'view'})
    surf_report_markdown=md(str(headlines).replace("<div class=\"views-field views-field-title\">","<p>Source : https://www.swellnet.com/reports/australia/new-south-wales/northern-beaches</p><div class=\"views-field views-field-title\">")\
                                          .replace("<span class=\"views-field","<br><span class=\"views-field")\
                                          .replace("<div class=\"field-content\">","<br><div class=\"field-content\">"))
    surf_report_tidy=surf_report_markdown.strip()
    print(surf_report_tidy)
    df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

    timestamp = datetime.now().strftime('%d-%m-%Y')
    title="{} Surf Report :: Swellnet".format(timestamp)
    url = surf_report_tidy
    df = df.append({
         "timestamp": timestamp,
         "title": title,
         "url": url,
         "posted": "False",
    }, ignore_index=True)


    # print(remote_url)
    # print_full(df)
    # print("==================================")

    csv = csv.append(df, ignore_index=True)
    csv.drop_duplicates(['title'],inplace=True)
    csv.to_csv(csv_file, index=False)


def publish_to_reddit():
    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    username      = cfg['reddit']['username']
    password      = cfg['reddit']['password']
    sub_reddit    = cfg['reddit']['sub_reddit']
    client_id     = cfg['reddit']['client_id']
    client_secret = cfg['reddit']['client_secret']
    user_agent    = cfg['reddit']['user_agent']

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
            wait_for=randint(120, 180)
            try:
                reddit.subreddit(sub_reddit).submit(title, selftext=url)
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
    surfreport()
    publish_to_reddit()

if __name__ == '__main__':
    main()
