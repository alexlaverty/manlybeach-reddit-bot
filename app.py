import requests
import urllib.request
import pandas as pd
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime


# Get Remote
#url = 'https://www.9news.com.au/manly'
#page = urllib.request.urlopen(url)
#soup = BeautifulSoup(page, 'html.parser')

# Get Local
soup = BeautifulSoup(open("index.html"), "html.parser")

rows = []

headlines = soup.find_all('h1', {'class' : 'story__headline'})

csv_file = "data.csv"

csv_exists = os.path.isfile(csv_file)

if not csv_exists:
    new_csv = pd.DataFrame(columns=["timestamp","title", "url","posted"])
    new_csv.to_csv(csv_file, index=False)

csv = pd.read_csv(csv_file)

df = pd.DataFrame(columns=["timestamp","title", "url","posted"])

for headline in headlines:
    # row=[,headline.find('a')['href']]
    # rows = row.append(row)
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

print("print df :")
print(df)

csv = csv.append(df, ignore_index=True)
csv.drop_duplicates(['url'],inplace=True)

print("CSV FILE :")
print(csv)

print("CSV Count : {}".format(str(len(csv))))

csv.to_csv(csv_file, index=False)
