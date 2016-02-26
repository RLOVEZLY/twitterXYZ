# Import the necessary package to process data in JSON format
try:
    import json
except ImportError:
    import simplejson as json

# Import the necessary methods from "twitter" library
from twitter import *
import sys
# Variables that contains the user credentials to access Twitter API 
ACCESS_TOKEN = '335637907-hO5rjVir6XVeo7adCKqZxAuQGMrQbOwG76hbvapO'
ACCESS_SECRET = '7VvAVR5M1nOpVKdsj6Zrwv78hXpPXBbE62OKE1JTcBtZq'
CONSUMER_KEY = '4mEWAvfATSJfmyAGGSVMdHqAP'
CONSUMER_SECRET = 'keRznRfKfup77SA4KFceQCzK9KnrWHysBf50LKxEWeIKS9R0sE'

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

# Initiate the connection to Twitter Streaming API
twitter_tl = Twitter(auth=oauth)

rationalThinker = []

with open("rationalPeople.txt") as f:
    w = f.read().splitlines()
for ww in w:
    ww = ww.strip(' \t\n\r')
    rationalThinker.append(ww)

emotionalThinker = []
with open("emotionalPeople.txt") as f:
    w1 = f.read().splitlines()
for ww1 in w1:
    ww1 = ww1.strip(' \t\n\r')
    emotionalThinker.append(ww1)


fr = open('./rationalTweets.txt', 'w+')
countR = 0

fe = open('./emotionalTweets.txt', 'w+')
countE = 0



for i in rationalThinker:

	#fr.write(i)
	#fr.write('\n')
	try:
		iterator = twitter_tl.statuses.user_timeline(screen_name=i, count = 150)
		maxidRList = []
		for tweet in iterator:
			countR = countR + 1
			maxidRList.append (long(json.dumps(tweet['id']))-1)
			#print json.dumps(tweet['text'])
			fr.write(json.dumps(tweet['text']))
			fr.write('\n')

		endR = False
		times = 19
		while not endR:
			maxidR = min(maxidRList)
			iterator = twitter_tl.statuses.user_timeline(screen_name=i, count = 150, max_id = maxidR)
			if len(iterator) == 0:
				endR = True

			for tweet in iterator:
				countR = countR + 1
				maxidRList.append(long(json.dumps(tweet['id']))-1)
				#print json.dumps(tweet['text'])
				fr.write(json.dumps(tweet['text']))
				fr.write('\n')

			times = times - 1
			if times == 0:
				break

	except:
		print "Exceed Limit"
print countR


for i in emotionalThinker:

	#fe.write(i)
	#fe.write('\n')
	try:
		iterator1 = twitter_tl.statuses.user_timeline(screen_name=i, count = 150)
		maxidEList = []
		for tweet in iterator1:
			countE = countE + 1
			maxidEList.append(long(json.dumps(tweet['id']))-1)
			#print json.dumps(tweet['text'])
			fe.write(json.dumps(tweet['text']))
			fe.write('\n')

		endE = False
		times = 19
		while not endE:
			maxidE = min(maxidEList)
			iterator1 = twitter_tl.statuses.user_timeline(screen_name=i, count = 150, max_id = maxidE)
			if len(iterator) == 0:
				endE = True

			for tweet in iterator1:
				countE = countE + 1
				maxidEList.append(long(json.dumps(tweet['id']))-1)
				#print json.dumps(tweet['text'])
				fe.write(json.dumps(tweet['text']))
				fe.write('\n')
			times = times - 1
			if times == 0:
				break
	except:
		print "except limit"


print countR
print countE
