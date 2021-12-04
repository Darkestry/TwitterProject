import matplotlib.pyplot as plt  # Data visualisation
import pandas as pd  # Data manipulation and analysis
import regex as re  # Data manipulation
import requests  # To create HTTP-GET-requests
import secret_data  # Twitter secret data

from time import sleep  # To delay HTTP-GET-requests from Twitter API
from selectolax.parser import HTMLParser  # Data Cleansing
from textblob_de import TextBlobDE  # Sentiment Analysis
from wordcloud import WordCloud, STOPWORDS  # Word Cloud


consumer_key = secret_data.consumer_key
consumer_secret = secret_data.consumer_secret

access_token = secret_data.access_token
access_token_secret = secret_data.access_token_secret

bearer_token = secret_data.bearer_token

search_url = "https://api.twitter.com/2/tweets/counts/all"
search_url2 = "https://api.twitter.com/2/tweets/search/all"

hashtag_list = ["#cdu", "#csu", "#spd", "#gruene", "#fdp", "#afd", "#dielinke"]  # Hashtags used to request the Twitter-API
start_time = "2021-07-01T00:00:00Z"  # Time from where historical Twitter data should be requested
end_time = "2021-10-01T00:00:00Z"  # Time until where historical Twitter data should be requested


def bearer_oauth(r):
    """
    Function required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"  # Bearer Authentication, refer to OAuth 2.0 in RFC 6750
    r.headers["User-Agent"] = "v2FullArchiveSearchPython"  # or v2RecentSearchPython for total_tweet_count().
    return r


def connect_to_endpoint(url, params):
    """
    Function to fire HTTP-GET-requests to the Twitter-API
    """
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()  # Return response-data in JSON-format


def total_tweet_count():
    """
    Function to count all occurrences of hashtags from July 1, 2021 to October 1, 2021 (92 days)
    """
    queries = []  # List of tweet counts per hashtag
    data = {"Party": ["CDU", "CSU", "SPD", "GRÜNE", "FDP", "AFD", "DIE LINKE"]}  # Dictionary for dataframe header
    df = pd.DataFrame(data)  # Create dataframe

    for hashtag in hashtag_list:
        query_params_list = [{'query': hashtag, 'granularity': 'day', 'start_time': '2021-07-01T00:00:00Z', 'end_time': '2021-08-01T00:00:00Z'},
                             {'query': hashtag, 'granularity': 'day', 'start_time': '2021-08-01T00:00:00Z', 'end_time': '2021-09-01T00:00:00Z'},
                             {'query': hashtag, 'granularity': 'day', 'start_time': '2021-09-01T00:00:00Z', 'end_time': '2021-10-01T00:00:00Z'}]

        tweet_count = 0  # Reset tweet count variable

        for query in query_params_list:
            json_response = connect_to_endpoint(search_url, query)
            tweet_count += json_response["meta"]["total_tweet_count"]  # Search for total tweet count of each hashtag in JSON-response

        queries.append(tweet_count)

    df["tweet_count"] = queries  # Add column from list to dataframe

    #  Data Visualisation
    plt.bar(df["Party"], df["tweet_count"], color=["black", "black", "red", "green", "yellow", "blue", "magenta"])
    plt.xticks(rotation=0, horizontalalignment="center")
    plt.title("Tweet count per party during preelection")
    plt.show()


def main():
    """
    Function to collect and cleanse all tweets of predefined hashtags from July 1, 2021 to October 1, 2021 (92 days)
    """
    tweet_list = []
    counter = 0  # Progress counter
    for hashtag in hashtag_list:
        print(f"Processing {hashtag}")
        query = {'query': hashtag, 'start_time': start_time, 'end_time': end_time, 'max_results': '500'}  # Query parameters
        json_response = connect_to_endpoint(search_url2, query)
        print(json_response)
        try:
            for tweet in json_response["data"]:
                tweet_list.append((hashtag, tweet["text"]))  # Append tuple of tweet text and their corresponding hashtag to list
                counter += 1
                if counter % 5000 == 0:
                    print(f"Processed {counter} tweets...")
        except Exception as e:
            print(repr(e))
        sleep(3)  # Wait 3 seconds between each request in order to work around Twitter-API limits
        while len(json_response["meta"]) > 3:  # If there are more than 500 tweets available, adjust query parameters
            query = {'query': hashtag, 'start_time': start_time, 'end_time': end_time,
                     'max_results': '500', 'next_token': json_response["meta"]["next_token"]}
            json_response = connect_to_endpoint(search_url2, query)
            if json_response["meta"]["result_count"] > 0:  # Required to prevent empty response errors
                try:
                    for tweet in json_response["data"]:
                        tweet_list.append((hashtag, tweet["text"]))  # Append tuple of tweet text and their corresponding hashtag to list
                        counter += 1
                        if counter % 5000 == 0:
                            print(f"Processed {counter} tweets...")
                except Exception as e:
                    print(repr(e))
            sleep(3)  # Wait 3 seconds between each request in order to work around Twitter-API limits
        print(f"Processed {hashtag}")

    df = pd.DataFrame(tweet_list, columns=['Hashtag', 'Text'])  # Create dataframe with columns Hashtag, Text and fill it with tuples of tweet_list

    #  Data Cleansing using regular expressions
    df.apply(lambda x: HTMLParser(x['Text']).body.text(separator=' ').replace('\n', ' '), axis=1)  # Convert HTML to plain text
    df['Text'] = df['Text'].str.replace('[^\\w\\s#@/:%.,?!_-]', '', flags=re.UNICODE, regex=True)  # Remove emojis
    df['Text'] = df['Text'].replace(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', regex=True).replace(r'www\\S+', '', regex=True)  # Remove URLs
    df['Text'] = df['Text'].replace('@', '', regex=True)  # Remove @-symbols
    df['Text'] = df['Text'].replace('#', '', regex=True)  # Remove #-symbols
    df['Text'] = df['Text'].str.replace('\n', '', regex=True)  # Remove line breaks
    df['Text'] = df['Text'].str.replace('\t', ' ')  # Replace tabulation with normal whitespace
    df['Text'] = df['Text'].str.replace(' {2,}', ' ', regex=True)  # Replace 2 or more spaces with normal whitespace
    df['Text'] = df['Text'].str.strip()  # Remove any leading and trailing space characters
    df.dropna()  # Remove empty rows

    df.to_csv(f"tweets_{hashtag}.csv", sep='\t', encoding='utf-8', index=False)  # Export dataframe to .CSV


def load_tweets_from_csv(party):
    """
    Function to read in .CSV files
    """
    df = pd.read_csv(f"tweets_{party}.csv", encoding="utf-8", sep="\t")
    return df


def create_wordcloud(party):
    """
    Function to create word clouds from tweets
    """
    df = load_tweets_from_csv(party)  # Import csv-file into dataframe

    stopwords = set(STOPWORDS)  # Create set of stopwords
    with open("stopwords.txt", "r") as fp:
        stopword_list = [''.join(line.strip("\n")) for line in fp.readlines()]  # Load stopwords from stopwords file
    stopwords.update(stopword_list)

    # Generate and visualise word cloud
    wordcloud = WordCloud(width=1900, stopwords=stopwords, height=1000, max_font_size=175, max_words=50, collocations=False, background_color='black').generate(str(df[df['Hashtag'].str.match("#" + party)]["Text"]))
    plt.figure(figsize=(50, 40))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title(f"Word cloud for hashtag: #{party}\nTime inverval: {start_time} until {end_time}", fontdict={'fontsize': 75})
    plt.show()


def analyse_sentiment(party):
    """
    Function to perform sentiment analysis on tweets using the TextBlobDE module https://textblob-de.readthedocs.io/en/latest/
    """
    df = load_tweets_from_csv(party)
    tweets = df["Text"].astype(str)

    counter = 0  # Progress counter
    sentiment = []
    for tweet in tweets:
        sentence = TextBlobDE(tweet)  # Analyse sentiment
        sentiment.append(sentence.sentiment.polarity)  # Append polarity to list
        counter += 1
        if counter % 5000 == 0:
            print(f"Processed {counter} tweets...")

    df["Polarity"] = sentiment  # Add list as new column to dataframe, describing the tweet's polarity
    df.to_csv(f"tweets_{party}_sentiment.csv", sep='\t', encoding='utf-8', index=False)


if __name__ == "__main__":
    '''
    total_tweet_count()
    main()
    parties = ["cdu", "csu", "spd", "gruene", "fdp", "afd", "dielinke"]
    for party in parties:
        create_wordcloud(party) #  possible parameters: #cdu, #csu, #spd, #gruene, #fdp, #afd, #dielinke
        analyse_sentiment(party)
    '''

