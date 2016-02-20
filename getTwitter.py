# Import the necessary package to process data in JSON format
try:
    import json
except ImportError:
    import simplejson as json

# Import the necessary methods from "twitter" library
from twitter import *

# Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = '335637907-hO5rjVir6XVeo7adCKqZxAuQGMrQbOwG76hbvapO'
ACCESS_SECRET = '7VvAVR5M1nOpVKdsj6Zrwv78hXpPXBbE62OKE1JTcBtZq'
CONSUMER_KEY = '4mEWAvfATSJfmyAGGSVMdHqAP'
CONSUMER_SECRET = 'keRznRfKfup77SA4KFceQCzK9KnrWHysBf50LKxEWeIKS9R0sE'

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initiate the connection to Twitter Streaming API
twitter_tl = Twitter(auth=oauth)

iterator = twitter_tl.statuses.user_timeline(screen_name="jk_rowling")

for tweet in iterator:
    print json.dumps(tweet['text'])
    

