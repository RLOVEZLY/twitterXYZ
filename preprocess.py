import sys
import os
import re
import stemmer
import operator

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
	print emotionalDict
	print rationalDict

	

if __name__ == "__main__":
	main()












