import json
import regex as re
from time import sleep
import requests
import pandas as pd
import matplotlib.pyplot as plt

consumer_key = "iOWKyxGh5PrZwGR6w99Y1hbm1"
consumer_secret = "XszI78cpBY4ryDdHnSl1X4QCHNZ78mNFlQaXhrYkKZgw5zERDN"

access_token = "14517043-vXV9ySIfSN5Orho3DRQD6xeJ4ErRbcw0QrpIUJZz0"
access_token_secret = "lJN8xOtbkUwUk2oBO5yA6CWM1n74EafIE1E2S7x1M6T5V"

bearer_token = "AAAAAAAAAAAAAAAAAAAAACLxVAEAAAAAWSP6vNtCX%2BCHnWHe4%2BJKJS%2F5Suo%3Dk8eepd7q4hAk7IHFqHDSBPqwp2EdDcnzh2l79SN6Z6KZqghZ0w"

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
    queries = []
    data = {"Party": ["CDU", "CSU", "SPD", "GRÜNE", "FDP", "AFD", "DIE LINKE"]}

    hashtag_list = ["#cdu", "#csu", "#spd", "#gruene", "#fdp", "#afd", "#dielinke"]
    for hashtag in hashtag_list:
        query = {'query': hashtag, 'start_time': '2021-07-30T00:00:00Z', 'end_time': '2021-08-01T00:00:00Z', 'max_results': '500'}
        json_response = connect_to_endpoint(search_url2, query)
        tweet_list = []
        for tweet in json_response["data"]:
            tweet_list.append((hashtag, tweet["text"]))
        sleep(2)
        while len(json_response["meta"]) > 3:
            query = {'query': hashtag, 'start_time': '2021-07-31T22:00:00Z', 'end_time': '2021-08-01T00:00:00Z',
                     'max_results': '500', 'next_token': json_response["meta"]["next_token"]}
            json_response = connect_to_endpoint(search_url2, query)
            if json_response["meta"]["result_count"] > 0:
                for tweet in json_response["data"]:
                    tweet_list.append((hashtag, tweet["text"]))
            sleep(2)
    df = pd.DataFrame(tweet_list, columns=['Hashtag', 'Text'])
    pd.options.display.max_colwidth = 200
    print(df.head())

    regex_pattern = re.compile(pattern="["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                       "]+", flags=re.UNICODE)
    match = ""
    for text in df["Text"]:
        match += re.sub(regex_pattern, '', text)  # replaces pattern with ''
        pattern = re.compile(r'(https?://)?(www\.)?(\w+\.)?(\w+)(\.\w+)(/.+)?')
        match = re.sub(pattern, '', text)
        re_list = ['@[A-Za-z0–9_]+', '#']
        combined_re = re.compile( '|'.join( re_list) )
        match = re.sub(combined_re,'',text)
    print(match)


if __name__ == "__main__":
    main()