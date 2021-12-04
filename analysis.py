import matplotlib.pyplot as plt
import pandas as pd

außenpolitik = ["Bündnis", "Demokratie", "Russland", "China"]
wirtschaft = ["Haushalt", "Schulden", "Bürokratie", "Steuerentlastung"]
wirtschaft2 = ["Schwarze Null", "Solidaritätszuschlag", "Entfesselungspaket", "Minijob"]
gesundheit = ["Arzt", "Digitalisierung", "RKI", "Pharma", "Pflege"]
mobilität = ["Zug", "Tempolimit"]
soziales = ["Geringverdiener", "Rente", "Rassismus", "Rassist"]
soziales2 = ["Grundeinkommen", "Freibetrag", "Altersvorsorge", "alleinerziehend"]
bildung = ["Aufstieg", "Kita", "Bildung", "Studium", "BAföG"]
wohnen = ["Wohnung", "Miete", "Mietendeckel", "Wohnungsbau"]
klimaschutz = ["klimaneutral", "2030", "Treibhaus"]
ereignisse = ["Laschet", "Kanzler", "Merkel"]
ereignisse2 = ["Flut", "Söder", "Corona", "2G|3G", "Lockdown"]

dict_of_branches = {"Außenpolitik": außenpolitik,
                    "Bildung": bildung,
                    "Gesundheit": gesundheit,
                    "Ereignisse": ereignisse,
                    "Klimaschutz": klimaschutz,
                    "Mobilität": mobilität,
                    "Soziales": soziales,
                    "Soziales2": soziales2,
                    "Wirtschaft": wirtschaft,
                    "Wirtschaft2": wirtschaft2,
                    "Wohnen": wohnen}

"""
Data Visualisation of sentiment analysis
"""
for name, branch in dict_of_branches.items():
    print(f"Analysis of: {branch}\n")
    df_combined = pd.DataFrame()
    for idx, topic in enumerate(branch):
        df = pd.read_csv("tweets_cdu_sentiment.csv", encoding="utf-8", sep="\t")
        if topic != "None":
            df = df[df["Text"].str.contains(topic, na=False, case=False)]  # Filter tweets containing provided topic

        print(f"\nKeyword: {topic}")

        ptweets = df[df["Polarity"] > 0]
        ppercent = round((ptweets.shape[0] / df.shape[0] * 100), 1)
        print(f"Positive tweets: {ppercent} %, Count: {ptweets.shape[0]}")

        ntweets = df[df["Polarity"] < 0]
        npercent = round((ntweets.shape[0] / df.shape[0] * 100), 1)
        print(f"Negative tweets: {npercent} %, Count: {ntweets.shape[0]}")

        neutraltweets = df[df["Polarity"] == 0]
        neutralpercent = round((neutraltweets.shape[0] / df.shape[0] * 100), 1)
        print(f"Neutral tweets: {neutralpercent} %, Count: {neutraltweets.shape[0]}")

        df = pd.DataFrame({"Positive": ptweets.shape[0], "Neutral": neutraltweets.shape[0], "Negative": ntweets.shape[0]}, index=[topic])
        df_combined = df_combined.append(df)

    df_combined.plot.bar(stacked=True, title=f"Branch: {name}", rot=0, color=["green", "black", "red"])
    plt.rcParams["figure.autolayout"] = True
    plt.rcParams["figure.dpi"] = 144
    plt.xlabel("Keyword")
    plt.ylabel("Count")
    plt.show()
    print(f"\n")








