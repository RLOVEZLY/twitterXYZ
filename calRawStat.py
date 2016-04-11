import sys
import os
import math
import operator
import re

with open("rationalTweets98440.txt") as f:
	numTweet = 0;
	numWord = 0;
	vocab = set([])
	for line in f:
		numTweet += 1
		line = line.strip()
		line = line[1 : -1]
		tokenList = re.split(' ', line)
		for token in tokenList:
			vocab.add(token)
			numWord += 1

	print "Total tweets:", numTweet
	print "Average word per tweet:", numWord / float(numTweet)
	print "Total words:", numWord
	print "Total vocabulary:", len(vocab)





