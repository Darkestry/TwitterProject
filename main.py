import json
import regex as re
from time import sleep
import requests
import pandas as pd
import matplotlib.pyplot as plt
from selectolax.parser import HTMLParser
from wordcloud import WordCloud, STOPWORDS
from datetime import datetime

consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""

bearer_token = ""

search_url = "https://api.twitter.com/2/tweets/counts/all"
search_url2 = "https://api.twitter.com/2/tweets/search/all"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"  # or v2RecentSearchPython for total_tweet_count().
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def total_tweet_count():
    queries = []
    data = {"Party": ["CDU", "CSU", "SPD", "GRÜNE", "FDP", "AFD", "DIE LINKE"]}
    df = pd.DataFrame(data)
    hashtag_list = ["#cdu", "#csu", "#spd", "#gruene", "#fdp", "#afd", "#dielinke"]
    for hashtag in hashtag_list:
        query_params_list = [{'query': hashtag, 'granularity': 'day', 'start_time': '2021-07-01T00:00:00Z', 'end_time': '2021-08-01T00:00:00Z'},
                             {'query': hashtag, 'granularity': 'day', 'start_time': '2021-08-01T00:00:00Z', 'end_time': '2021-09-01T00:00:00Z'},
                             {'query': hashtag, 'granularity': 'day', 'start_time': '2021-09-01T00:00:00Z', 'end_time': '2021-10-01T00:00:00Z'}]
        tweet_count = 0
        for query in query_params_list:
            json_response = connect_to_endpoint(search_url, query)
            tweet_count += json_response["meta"]["total_tweet_count"]
        queries.append(tweet_count)
    df["tweet_count"] = queries
    plt.bar(df["Party"], df["tweet_count"], color=["black", "black", "red", "green", "yellow", "blue", "magenta"])
    plt.xticks(rotation=0, horizontalalignment="center")
    plt.title("Tweet count per party during preelection")
    plt.show()


def main():
    hashtag_list = ["#cdu", "#csu", "#spd", "#gruene", "#fdp", "#afd", "#dielinke"]
    tweet_list = []
    counter = 0
    for hashtag in hashtag_list:
        print(f"Processing {hashtag}")
        query = {'query': hashtag, 'start_time': '2021-07-01T00:00:00Z', 'end_time': '2021-10-01T00:00:00Z', 'max_results': '500'}
        json_response = connect_to_endpoint(search_url2, query)
        try:
            for tweet in json_response["data"]:
                tweet_list.append((hashtag, tweet["text"]))
                counter += 1
                if counter % 5000 == 0:
                    print(f"Processed {counter} tweets...")
        except Exception as e:
            print(repr(e))
        sleep(3)
        while len(json_response["meta"]) > 3:
            query = {'query': hashtag, 'start_time': '2021-07-01T00:00:00Z', 'end_time': '2021-10-01T00:00:00Z',
                     'max_results': '500', 'next_token': json_response["meta"]["next_token"]}
            json_response = connect_to_endpoint(search_url2, query)
            if json_response["meta"]["result_count"] > 0:
                try:
                    for tweet in json_response["data"]:
                        tweet_list.append((hashtag, tweet["text"]))
                        counter += 1
                        if counter % 5000 == 0:
                            print(f"Processed {counter} tweets...")
                except Exception as e:
                    print(repr(e))
            sleep(3)
        print(f"Processed {hashtag}")

    df = pd.DataFrame(tweet_list, columns=['Hashtag', 'Text'])
    pd.options.display.max_colwidth = 500

    df.apply(lambda x: HTMLParser(x['Text']).body.text(separator=' ').replace('\n', ' '), axis=1)
    df['Text'] = df['Text'].str.replace('[^\w\s#@/:%.,_-]', '', flags=re.UNICODE, regex=True)  #
    df['Text'] = df['Text'].replace(r'http\S+', '', regex=True).replace(r'www\S+', '', regex=True)  # remove URLs from tweets
    df['Text'] = df['Text'].replace('@[A-Za-z0–9_]+', '', regex=True)
    df['Text'] = df['Text'].replace('#[A-Za-z0–9_]+', '', regex=True)
    df['Text'] = df['Text'].str.replace('\n', '', regex=True)
    df['Text'] = df['Text'].str.replace('\t', ' ')
    df['Text'] = df['Text'].str.replace(' {2,}', ' ', regex=True)
    df['Text'] = df['Text'].str.strip()
    df.dropna()
    #  df.to_csv("tweets3.csv", sep='\t', encoding='utf-8', index=False)    saves all tweets to a .csv file 

    stopwords = set(STOPWORDS)
    with open("stopwords.txt", "r") as fp:
        stopword_list = [''.join(line.strip("\n")) for line in fp.readlines()]
    stopwords.update(stopword_list)

    for tag in hashtag_list:
        wordcloud = WordCloud(width=1600, stopwords=stopwords, height=800, max_font_size=200, max_words=50, collocations=False, background_color='black').generate(str(df[df['Hashtag'].str.match(tag)]["Text"]))
        plt.figure(figsize=(40, 30))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")
        plt.title(f"Word cloud for hashtag: {tag}\nTime inverval: {query['start_time']} until {query['end_time']}", fontdict={'fontsize': 75})
        plt.show()


if __name__ == "__main__":
    main()
