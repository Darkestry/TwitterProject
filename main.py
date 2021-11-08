import requests
import json
import pandas as pd
import matplotlib.pyplot as plt


consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""

bearer_token = ""

search_url = "https://api.twitter.com/2/tweets/counts/all"


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


def main():
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


if __name__ == "__main__":
    main()
