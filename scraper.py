from urllib import request
import tweepy
import requests
import json
import csv
import re, os
import time

import twint

consumer_key = *insert consumer key*
consumer_secret = *insert secret consumer key*
access_key = *insert api access key*
access_secret = *insert api secret access key*
bearer_token = *insert bearer token*


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
client = tweepy.Client( bearer_token=bearer_token, 
                        consumer_key=consumer_key, 
                        consumer_secret=consumer_secret, 
                        access_token=access_key, 
                        access_token_secret=access_secret, 
                        return_type = requests.Response,
                        wait_on_rate_limit=True)  
    
auth.set_access_token(access_key, access_secret)

api = tweepy.API(auth, retry_count = 10, retry_delay = 60, parser=tweepy.parsers.JSONParser(), wait_on_rate_limit = True)


def create_headers():
    headers = {"Authorization": "Bearer {}".format(bearer_token), 'user-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36'}
    return headers

def create_url(headers, id, next_token = None):
    url = "https://api.twitter.com/2/tweets/"+ id + "/retweeted_by" 
    response = requests.request("GET", url, headers = headers, params = {"pagination_token": next_token})    
    return (response.json())

def get_tweets(username):

    c = twint.Config()      #twint configuration
    c.User_id = username
    c.Store_csv = True
    c.Output = *insert output file name*
    c.Resume = "search.txt"
    c.Limit = 100
    c.Hide_output = True

    for i in range(1):
        try: twint.run.Search(c)
        except: continue
    
    if os.path.exists('search.txt'): os.remove('search.txt')

def openFile():
    res = {}
    total = []

    with open (*insert input csv file*, encoding='cp437') as f:
        reader = csv.DictReader(f)

        for row in reader:
            user_id = (list((row.values())))[6]
            name = (list((row.values())))[7]
            tweet_id = (list((row.values())))[0]
            if 'user_id' not in res or res['user_id'] != user_id:
                res = {}
                print(user_id)
                res['user_id'] = user_id
                res['screen_name'] = name
                total.append(res)
            if 'tweets' not in res: res['tweets'] = [likesAndRetweets(tweet_id, name, row)]
            else: res['tweets'].append(likesAndRetweets(tweet_id, name, row))
            
            with open('beyonceinfo2.json', 'w') as outf:
                outf.write(json.dumps(total))                
    
    f.close()   

def likesAndRetweets(strings, name, row):

    try:        
        tweet = {}                   
        tweet['data'] = (row)  # tweet info

        response = (client.get_liking_users(strings).json())    #liking users        
        if response and 'data' in response: tweet['likers'] = [response['data']]   

        for i in range(2):
            if response and 'meta' in response and 'next_token'in response and response['data'] not in tweet['likers']: tweet['likers'].append(client.get_liking_users(strings, pagination_token = response["meta"]['next_token'] ).json()['data'])
        
        headers = create_headers()  #auth header
        tweet['retweeters'] = []

        next_token = None            
        for i in range(5):
            response = (create_url(headers, strings, next_token))  # retweeter loop
            try:
                if response and response['meta'] and 'next_token' in response: next_token = response['meta']['next_token']
                if 'data' in response and response['data'] not in tweet['retweeters']: tweet['retweeters'].append(response['data'])
            except:
                print('Retrying')
                time.sleep(800)
                continue       

    except:
        print('Error sleep')
        time.sleep(120)

    return tweet  

def check():
    with open (*insert output file path*, 'r') as f:
        data = json.load(f)
    f.close()

    tweetLen = []
    likes = []
    retweets = []

    for i in range(len(data)):
        tweets = (data[i]['tweets'])
        tweetLen.append(len(tweets))
        for tweet in tweets:
            if 'likers' in tweet: likes.append(len(tweet['likers'][0]))
            if 'retweeters' in tweet and tweet['retweeters']: retweets.append(len(tweet['retweeters'][0]))
    print(sum(tweetLen), sum(likes), sum(retweets))
    

if __name__ == '__main__':
    with open (*insert input csv file name*, encoding='cp437') as f:
        reader = csv.DictReader(f) 

        for row in reader:
            strings =  (list((row.values())))[0]
            print(strings)
            
            ##regex required when account number does not appear under a specific column under csv file
            
            # regex = '(\S*)[\t]'

            # data = re.findall(regex, strings)
            # # if data and data[0]: print(data[0])

            # pattern = "\d+[.]?\d*"
            # if data and data[0]:
            #     id = re.findall(pattern, data[0])
            #     if id:
            #         print(str(id[0]))
            get_tweets(strings)
    f.close()
    # openFile()        
    check()
