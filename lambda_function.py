import json, time, tweepy, os
from os import environ
import boto3
import tempfile
import botocore
from twython import Twython, TwythonError

CONSUMER_KEY = environ['CONSUMER_KEY']
CONSUMER_SECRET = environ['CONSUMER_SECRET']
ACCESS_KEY = environ['ACCESS_KEY']
ACCESS_SECRET = environ['ACCESS_SECRET']
AACCESS_KEY = environ['AACCESS_SECRET']
SECRET_KEY = environ['SECRET_KEY']
BUCKET_NAME = environ['BUCKET_NAME']
KEY = environ['KEY']

s3 = boto3.resource('s3', aws_access_key_id=AACCESS_KEY, aws_secret_access_key=SECRET_KEY) #503 error
bucket= s3.Bucket(BUCKET_NAME)

def lambda_handler(event, context):
    search_tweet()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

def search_tweet():

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET)
    
    # Create API object
    api = tweepy.API(auth)
    
    # Create a tweet
    tweets = api.mentions_timeline()
    for tweet in tweets:
    	if tweet.favorited == False:
    	    client = boto3.client('iot-data')
    	    client.publish(topic='opensolenoid', qos=1)
    	    client.publish(topic='takepicture', qos=1)
    	    status = "Thank you! @" + str(tweet.user.screen_name) + " for watering on " + str(tweet.created_at)
    	    print(tweet.text)
    	    tmp_dir = tempfile.gettempdir()
    	    path = os.path.join(tmp_dir, KEY)
    	    print("created directory at " + path)
    	    s3.Bucket(BUCKET_NAME).download_file(KEY, path)
    	    print('file moved to temp directory')
    	    with open(path, 'rb') as img:
    	        twit_resp = twitter.upload_media(media=img)
    	        status = "Thank you @" + str(tweet.user.screen_name) + " for watering on " + str(tweet.created_at)
    	        twitter.update_status(status=status, media_ids=twit_resp['media_id'])
    	        tweet.favorite()
