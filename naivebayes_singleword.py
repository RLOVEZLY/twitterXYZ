import sys
import os
import re
import stemmer
import operator
import math
import pickle

def replaceAT(text):
	text = re.sub(r'@[^ ]* ', r'ATATAT ', text)
	return text



def replaceHashtag(text):
	text = re.sub(r'#[^ ]* ', r'HASHTAG ', text)
	return text



def removeURL(text):
	text = re.sub(r'http://[^ ]* ', r'URLURL ', text)
	text = re.sub(r'https://[^ ]* ', r'URLURL ', text)
	return text



def tokenizeText(text):

	# remove all characters other than alphanumeric characters and 
	# punctuations with special cases ('\.', '\'', '-', ',', '/')
	text = re.sub(r'[^A-Za-z0-9.,\'-/]', r' ', text)



	# date
	# format1: 12/12/2015 (keep them together, i.e. "2 /13/ 2014" -> "2/13/2014")
	text = re.sub(r'([0-9]{1,2}) {0,1}/ {0,1}([0-9]{1,2}) {0,1}/ {0,1}([0-9]{2,4})', r'\1/\2/\3', text)
	# clean up unused "/"
	occ_slash = [m.start() for m in re.finditer(r'/', text)]
	# if slash has alphanumeric characters on both sides, we consider this "/" to be useful
	for pos in occ_slash:
		if not text[pos - 1].isalnum() or not text[pos + 1].isalnum():
			text = text[ : pos] + ' ' + text[pos + 1 : ]

	# format2: jan. 15, 2015 or january 15, 2015 -> jan./15/2015
	# Note: we use / in the final version to split month, day, and year. 
	#       Since we have already removed all meaningless slash in the 
	#       previous step, the slashes from this step will go with tokens.
	monthList = ["jan\.", "january", "feb\.", "february", "march", "april", "apr\.", "may", "june", "july", "august", "aug\.", "sep\.", "september", "october", "oct\.", "november", "nov\.", "december", "dec\."]
	for month in monthList:
		text = re.sub(month + r' {1}([0-9]{1,2}), ([0-9]{4})', month + r'/\1/\2', text)


	

	# ','
	occ_quote = [m.start() for m in re.finditer(',', text)]
	for pos in occ_quote:
		# we treat this comma as a separator in a number, only if the three characters after the comma are digits, the forth is not a digit, and the previous is a digit.
		# e.g. "1,000" will be treated as a number. "1,0000" and ",233" will not.
		if text[pos + 1 : pos + 4].isdigit() and text[pos - 1].isdigit() and not text[pos + 4].isdigit():
			continue
		# replace other "," with a space
		else :
			text = text[ : pos] + ' ' + text[pos + 1 : ]




	# '-'
	occ_quote = [m.start() for m in re.finditer('-', text)]
	# we will treat words on the left and right side of "-" as a phrase, 
	# only if these two words are closely connected, i.e. the previous and 
	# following characters are both alphanumeric
	for pos in occ_quote:
		if text[pos - 1].isalnum() and text[pos + 1].isalnum():
			continue
		# replace with a space otherwise
		else :
			text = text[ : pos] + ' ' + text[pos + 1 : ]
			continue



	# '\''
	# remove '\'' if it represents a single quotation
	text = re.sub(r' [\']([^\']+)[\']', r' \1 ', text)
	# separate the possessive
	# Note: "'s" means the possessive, including "'s" and "s'", i.e. "students'"
	# will be tokenized as ["students", "'s"]. In this case, "'s" means a possessive 
	# appears as a token
	text = re.sub(r'([a-z0-9]+[sz])(\') ', r'\1 \2s ', text)
	text = re.sub(r'([a-z0-9]+)(\'s )', r'\1 \2', text)
	# find possible omissions and replace them accordingly
	# Note: cannot distinguish possessive from omission, e.g. "dog's"
	omissionPair = [[" won't ", " will not "], [" I'm ", " I am "], ["'re ", " are "], ["'ve ", " have "], ["'ll ", " will "], ["n't ", " not "]]
	for pair in omissionPair:
		text = text.replace(pair[0], pair[1])



	
	# "\."
	# eliminate space between digit and dot. For example, "1 .3" and 
	# "1. 3" will be converted to "1.3"
	text = re.sub(r'[ ]([0-9]+)[ ]{,1}\.[ ]{,1}([0-9]+)[ ]', r' \1.\2 ', text) 
	occ_dot = [m.start() for m in re.finditer('\.', text)]
	for pos in occ_dot:
		# Acronyms and Abbreviation: if the previous and following characters are both alphabetical
		# charaters, we will treat it as a acronym or abbreviation
		if text[pos - 1].isalpha() and text[pos + 1].isalpha():
			continue
		# if both previous and following characters are digits,  we treat it as a 
		# decimal number. Note that this cannot filter out "1.3.4". However, it is 
		# possible that one of the comma is a period. So we may not be able to 
		# completely solve this case.
		elif text[pos - 1].isdigit() and text[pos + 1].isdigit():
			continue
		# if it is neither an acronyms/abbreviation nor a decimal number, we 
		# will replace this dot with a space.
		else :
			text = text[ : pos] + ' ' + text[pos + 1 : ]


	# After all steps above, we replace all useless characters with a space. 
	# we will split the text with " ". Each item will be a token.
	text = text.strip()
	tokenList = re.split('\s+', text)

	return tokenList

def removeStopwords(tokenList):
	with open('stopwords') as f:
		stopwords = f.readlines()
	stopwords = [word.strip() for word in stopwords]
	# remove stopwords from tokens
	tokenList = [word for word in tokenList if word not in stopwords]
	return tokenList


def stemWords(tokenList):
	p = stemmer.PorterStemmer()
	stemmedList = []
	for word in tokenList: 
		prevWord = ""
		# stem the token until it doesn't change any more.
		while word != prevWord:
			prevWord = word;
			word = p.stem(word, 0, len(word) - 1)
		stemmedList.append(word);

	return stemmedList

def trainNaiveBayes(rational_tweets, emotional_tweets, level_type):
    rational_word_count = {}
    emotional_word_count = {}
    rational_cond_prob = {}
    emotional_cond_prob = {}
    rational_doc_num = 0
    emotional_doc_num = 0
    vocab = set([])
    
    if level_type == "user":
        rational_doc_num = len(rational_tweets)
        emotional_doc_num = len(emotional_tweets)
    elif level_type == "tweet":
        for tweets in rational_tweets.values():
            rational_doc_num += len(tweets)
        for tweets in emotional_tweets.values():
            emotional_doc_num += len(tweets)
    # calculate class probabilities
    rational_prob = math.log10(1.0 * rational_doc_num / (rational_doc_num + emotional_doc_num))
    emotional_prob = math.log10(1.0 * emotional_doc_num / (rational_doc_num + emotional_doc_num))
    
    rational_user_count = 0
    emotional_user_count = 0
    
    for tweets in rational_tweets.values():
        rational_user_count += 1
        #print "rational user " + str(rational_user_count)
        for tweet in tweets:
            for word in tweet:
                vocab.add(word)
                rational_word_count[word] = rational_word_count.get(word, 0) + 1
    
    for tweets in emotional_tweets.values():
        emotional_user_count += 1
        #print "emotional user " + str(emotional_user_count)
        for tweet in tweets:
            for word in tweet:
                vocab.add(word)
                emotional_word_count[word] = emotional_word_count.get(word, 0) + 1
    
    #calculate conditional probabilities
    vocab_size = len(vocab)
    rational_total_word_count = sum(rational_word_count.values())
    emotional_total_word_count = sum(emotional_word_count.values())
    for w in vocab:
        rational_cond_prob[w] = math.log10(float(rational_word_count.get(w,0) + 1) / (rational_total_word_count + vocab_size))
        emotional_cond_prob[w] = math.log10(float(emotional_word_count.get(w,0) + 1) / (emotional_total_word_count + vocab_size))
        
    # calculate conditional probability of a word if it does not occur in training tweets
    rational_absent_cond_prob = math.log10(1.0 / (rational_total_word_count + vocab_size))
    emotional_absent_cond_prob = math.log10(1.0 / (emotional_total_word_count + vocab_size))
    
    """
    print "rational_prob = " + str(rational_prob)
    print "emotional_prob = " + str(emotional_prob)
    print "rational_cond_prob:"
    print rational_cond_prob 
    print "emotional_cond_prob:"
    print emotional_cond_prob
    print "rational_absent_cond_prob = " + str(rational_absent_cond_prob)
    print "emotional_absent_cond_prob = " + str(emotional_absent_cond_prob)
    """
    
    return rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob
                
def testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, level_type, test_tweets):
    if level_type == "user":
        rational_log_sum = rational_prob
        emotional_log_sum = emotional_prob
        for tweet in test_tweets:
            for w in tweet:
                if w in rational_cond_prob:
                    rational_log_sum += rational_cond_prob[w]
                    emotional_log_sum += emotional_cond_prob[w]
                else:
                    rational_log_sum += rational_absent_cond_prob
                    emotional_log_sum += emotional_absent_cond_prob
        #print "rational_log_sum = " + str(rational_log_sum)
        #print "emotional_log_sum = " + str(emotional_log_sum)
        if rational_log_sum < emotional_log_sum:
            return "emotional"
        else:
            return "rational"
    elif level_type == "tweet":
        # keep a score to record result of each tweet. If a tweet is classified as rational, add one to score;
        # otherwise, subtract one from score. After all tweets are classified, the person is classified as 
        # rational if the score is positive; emotional if the score is negative.
        #print "# of tweets: " + str(len(test_tweets))
        score = 0
        for tweet in test_tweets:
            rational_log_sum = rational_prob
            emotional_log_sum = emotional_prob
            for w in tweet:
                if w in rational_cond_prob:
                    rational_log_sum += rational_cond_prob[w]
                    emotional_log_sum += emotional_cond_prob[w]
                else:
                    rational_log_sum += rational_absent_cond_prob
                    emotional_log_sum += emotional_absent_cond_prob
            #print "rational_log_sum = " + str(rational_log_sum)
            #print "emotional_log_sum = " + str(emotional_log_sum)
            if rational_log_sum < emotional_log_sum:
                score -= 1
            else:
                score += 1
        
        #print "score = " + str(score)
        if score < 0:
            return "emotional"
        elif score > 0:
            return "rational"
        else:
            return "cannot classify"


def main():
	docNames = os.listdir('data')
	emotionalDict = {}
	rationalDict = {}
	for docName in docNames:
		username = docName[0: -6]
		infile = open('data/' + docName)
		text = infile.read()
		tweets = re.findall('"([^"]*)"\n', text)
		if docName[-5] == 'E':
			emotionalDict[username] = []
		elif docName[-5] == 'R':
			rationalDict[username] = []
		else:
			print "Cannot recognize type: ", docName[-1]
		#print len(tweets)
		for twt in tweets:
			twt = twt.lower() + ' '
			twt = replaceAT(twt)
			twt = replaceHashtag(twt)
			twt = removeURL(twt)
			tokenList = tokenizeText(twt)
			tokenList = removeStopwords(tokenList)
			tokenList = stemWords(tokenList)
			if docName[-5] == 'E':
				emotionalDict[username].append(tokenList)
			elif docName[-5] == 'R':
				rationalDict[username].append(tokenList)

	# here are the two dictionaries: key: username, value: list of list of tokens
	emotional_tweet_count = 0
	rational_tweet_count = 0
	for tweets in emotionalDict.values():
		emotional_tweet_count += len(tweets)
	for tweets in rationalDict.values():
		rational_tweet_count += len(tweets)      

	#print "emotional tweets count = " + str(emotional_tweet_count)
	#print "rational tweets count = " + str(rational_tweet_count)

	emotional_names = emotionalDict.keys()
	rational_names = rationalDict.keys()
	train_emotional_names = {}
	test_emotional_names = {}
	train_rational_names = {}
	test_rational_names = {}
	#train_emotional_names[0] = emotional_names[0:40]
 	#train_rational_names[0] = rational_names[0:40] 
	
 	train_emotional_names[0] = emotional_names[5:40]
 	train_emotional_names[1] = emotional_names[0:5] + emotional_names[10:40]
 	train_emotional_names[2] = emotional_names[0:10] + emotional_names[15:40]
 	train_emotional_names[3] = emotional_names[0:15] + emotional_names[20:40]
 	train_emotional_names[4] = emotional_names[0:20] + emotional_names[25:40]
 	train_emotional_names[5] = emotional_names[0:25] + emotional_names[30:40]
 	train_emotional_names[6] = emotional_names[0:30] + emotional_names[35:40]
 	train_emotional_names[7] = emotional_names[0:35]
 	test_emotional_names[0] = emotional_names[0:5]
 	test_emotional_names[1] = emotional_names[5:10]
 	test_emotional_names[2] = emotional_names[10:15]
 	test_emotional_names[3] = emotional_names[15:20]
 	test_emotional_names[4] = emotional_names[20:25]
 	test_emotional_names[5] = emotional_names[25:30]
 	test_emotional_names[6] = emotional_names[30:35]
 	test_emotional_names[7] = emotional_names[35:40]
  
 	train_rational_names[0] = rational_names[5:40]
 	train_rational_names[1] = rational_names[0:5] + rational_names[10:40]
 	train_rational_names[2] = rational_names[0:10] + rational_names[15:40]
 	train_rational_names[3] = rational_names[0:15] + rational_names[20:40]
 	train_rational_names[4] = rational_names[0:20] + rational_names[25:40]
 	train_rational_names[5] = rational_names[0:25] + rational_names[30:40]
 	train_rational_names[6] = rational_names[0:30] + rational_names[35:40]
 	train_rational_names[7] = rational_names[0:35]
 	test_rational_names[0] = rational_names[0:5]
 	test_rational_names[1] = rational_names[5:10]
 	test_rational_names[2] = rational_names[10:15]
 	test_rational_names[3] = rational_names[15:20]
 	test_rational_names[4] = rational_names[20:25]
 	test_rational_names[5] = rational_names[25:30]
 	test_rational_names[6] = rational_names[30:35]
 	test_rational_names[7] = rational_names[35:40]
	
 	for i in range(8):
		print "ROUND " + str(i) 
 	 	train_emotional_dict = {}
 	 	for name in train_emotional_names[i]:
          	 	train_emotional_dict[name] = emotionalDict[name]

		train_rational_dict = {}
 		for name in train_rational_names[i]:
         		train_rational_dict[name] = rationalDict[name]
 
		rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob = trainNaiveBayes(train_rational_dict, train_emotional_dict, "user")
		"""
		with open('objs.pickle_preprocess', 'w') as f:
         		pickle.dump([rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob], f)

		with open('objs.pickle_preprocess') as f:
         		rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob = pickle.load(f)
           
           
		
		sorted_rational_words = sorted(rational_cond_prob, key=rational_cond_prob.get, reverse=True)
		sorted_emotional_words = sorted(emotional_cond_prob, key=emotional_cond_prob.get, reverse=True)
				
		print "Top 100 rational words:"
		for word in sorted_rational_words[0:100]:
        		print word + " " + str(pow(10,rational_cond_prob[word]))     
		print "Top 100 emotional words:"
		for word in sorted_emotional_words[0:100]:
        		print word + " " + str(pow(10,emotional_cond_prob[word]))
		"""  
		
		print "Testing rational people"
		print "user level"
		for name in test_rational_names[i]:
         		result = testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, "user", rationalDict[name])
         		print result
		print "tweet level"
		for name in test_rational_names[i]:
         		result = testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, "tweet", rationalDict[name])
         		print result
		print "Testing emotional people"
		print "user level"
		for name in test_emotional_names[i]:  
         		result = testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, "user", emotionalDict[name])
         		print result
		print "tweet level"
		for name in test_emotional_names[i]:  
         		result = testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, "tweet", emotionalDict[name])
         		print result
	

if __name__ == "__main__":
	main()












