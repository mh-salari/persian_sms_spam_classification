#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 11 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
@source: https://towardsdatascience.com/do-you-know-python-has-a-built-in-database-d553989c87bd

Search Twitter for images related to text SMS
"""

import snscrape.modules.twitter as sntwitter
from tqdm import tqdm
import tweepy
import wget
import os
import concurrent.futures
import pickle
import time
from datetime import datetime, timedelta
from config import *


def search_for_tweets(time):
    """search twitter for keyword, it search for tweets that have sent after the given time

    Args:
        time (str): search quarry time in y-m-d format [2017-01-01]

    Returns:
        id (list): list of ids of funded tweets
    """
    #  We search twitter for this keywords
    keywords = [
        "پیامک",
        "SMS",
        "اس ام اس",
        "پیام بابا",
        "پیام مامان",
    ]

    ids = list()
    for keyword in tqdm(keywords, position=0):
        search_query = f"'{keyword}' {time} lang:fa filter:images"
        for status in tqdm(
            sntwitter.TwitterSearchScraper(search_query).get_items(), leave=False
        ):
            ids.append(int(status.url.split("/")[-1]))

    return ids


def connect_to_twitter_api():
    """twitter authentication

    Returns:
        _tweepy API
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def download_tweet_media(api, id_, media_output_path):
    """download images of a tweets from its id

    Args:
        api (tweeter API):
        id_ (str): id of tweet
        media_output_path (str): output path for downloaded images

    Returns:
        (str): id of downloaded tweets_
    """
    tweet = api.get_status(id_, tweet_mode="extended")
    if "media" in tweet.entities:
        for media in tweet.extended_entities["media"]:
            image_url = media["media_url"]
            output_path = os.path.join(media_output_path, os.path.basename(image_url))
            # download image if we haven't downloaded yet
            if not os.path.exists(output_path):
                wget.download(image_url, output_path, bar=None)
    return id_


def main():

    # define required paths
    base_path = os.path.dirname(os.path.realpath(__file__))
    database_path = os.path.join(base_path, "database")
    media_output_path = os.path.join(database_path, "media")
    ids_pkl_path = os.path.join(database_path, "ids.pkl")
    saved_ids_path = os.path.join(database_path, "saved_ids.txt")

    # make required output path
    for path in [database_path, media_output_path]:
        if not os.path.exists(path):
            os.mkdir(path)

    # This part of code is a bit crazy!
    # if we haven't run this code yet, it start to search for tweets newer than 2017-01-01
    # otherwise, we search for tweets newer than last run of this code
    # this part of code set search_time based on above discretion
    SEARCH_FOR_NEW_TWEETS = False

    if os.path.exists(ids_pkl_path):
        last_search_time = datetime.fromtimestamp(os.path.getmtime(ids_pkl_path))
        yesterday = datetime.now() - timedelta(days=1)

        if yesterday >= last_search_time:
            SEARCH_FOR_NEW_TWEETS = True
            search_time = f"since:{last_search_time.strftime('%Y-%m-%d')} until:{datetime.now().strftime('%Y-%m-%d')}"

        else:
            print("Loading tweets id from the pkl file🦁")
            ids = pickle.load(open(ids_pkl_path, "rb"))
            ids = list(set(ids))
            ids.sort()
    else:
        SEARCH_FOR_NEW_TWEETS = True
        search_time = f"since: until:{datetime.now().strftime('%Y-%m-%d')}"

    print("Searching for new tweets🦦...\nsearch_time\n")
    if SEARCH_FOR_NEW_TWEETS:
        ids = search_for_tweets(search_time)
        pickle.dump(ids, open(ids_pkl_path, "wb"))

    if os.path.exists(saved_ids_path):
        with open(saved_ids_path, "r") as f:
            saved_ids = [int(line.rstrip("\n")) for line in f if line != "\n"]
            saved_ids = set(saved_ids)
    else:
        saved_ids = set()
    print(f"Downloaded: {len(saved_ids)}")

    new_ids_to_download = [id_ for id_ in ids if id_ not in saved_ids]
    print(f"To Download: {len(new_ids_to_download)}")

    api = connect_to_twitter_api()

    print("Downloading tweets media🦏...")
    print("-" * 30)
    # 900 requests over any 15-minute
    STOP = False
    pbar = tqdm(
        initial=len(saved_ids),
        total=len(new_ids_to_download) + len(saved_ids),
        leave=False,
    )
    while new_ids_to_download:
        pbar.set_postfix_str(f"Running")
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            future_to_id = {}
            futures = []
            for id_ in new_ids_to_download[:]:

                futures_executor = executor.submit(
                    download_tweet_media,
                    api=api,
                    id_=id_,
                    media_output_path=media_output_path,
                )
                future_to_id.update({futures_executor: id_})
                futures.append(futures_executor)

            done, not_done = concurrent.futures.wait(futures, timeout=0)
            while not_done:
                freshly_done, not_done = concurrent.futures.wait(not_done, timeout=1)
                done |= freshly_done
                for future in done:
                    id_ = future_to_id[future]
                    try:
                        data = future.result()
                    except tweepy.error.RateLimitError as exc:
                        STOP = True
                        pbar.set_postfix_str(f"Rate Limit Error!")
                    except concurrent.futures._base.CancelledError:
                        pass
                    except Exception as exc:
                        try:
                            # tweepy error
                            code = exc.args[0][0]["code"]
                            pbar.set_postfix_str(f"Last Tweepy error {code}")
                        except:
                            tqdm.write(f"{id_} generated an exception: {exc}")
                        new_ids_to_download.remove(id_)
                        with open(saved_ids_path, "a") as f:
                            f.write(f"{id_}\n")
                    else:
                        pbar.update(1)
                        new_ids_to_download.remove(id_)
                        with open(saved_ids_path, "a") as f:
                            f.write(f"{id_}\n")
                    if STOP:
                        for future in not_done:
                            _ = future.cancel()
                            # _ = concurrent.futures.wait(not_done, timeout=None)
                        break
                done = set()
        if STOP:
            sleep_time = timedelta(minutes=15, seconds=1)
            next_run = datetime.now() + sleep_time
            pbar.set_postfix_str(f"Sleep until {next_run.strftime('%H:%M:%S')}")
            time.sleep(sleep_time.total_seconds())
            STOP = False
    pbar.close()
    print("DON!")


if __name__ == "__main__":
    main()
