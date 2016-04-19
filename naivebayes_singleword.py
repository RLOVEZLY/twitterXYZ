# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 20:05:43 2016

@author: luyoujia
"""
import math

"""
rational_tweets and emotional_tweets are two dictionaries with username as key and list of list of strings as value.
level_type is either "user" or "tweet"
"""
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
        print "rational user " + str(rational_user_count)
        for tweet in tweets:
            for word in tweet:
                vocab.add(word)
                rational_word_count[word] = rational_word_count.get(word, 0) + 1
    
    for tweets in emotional_tweets.values():
        emotional_user_count += 1
        print "emotional user " + str(emotional_user_count)
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
        
        if score < 0:
            return "emotional"
        elif score > 0:
            return "rational"
        else:
            return "cannot classify"

def main():
    # just a simple test case
    rational_dict = {}
    emotional_dict = {}
    rational_dict["Amy"] = [["math", "is", "beautiful"], ["scientific", "equation"], ["mind", "blowing"]]
    rational_dict["Bob"] = [["calculate", "equation"], ["physics", "is", "beautiful"]]
    emotional_dict["Charles"] = [["I", "am", "so", "happy"], ["go", "go"]]
    emotional_dict["Daniel"] = [["this", "is", "good"], ["happy", "day"]]
    test = [["math", "is", "mind", "blowing"], ["good", "day", "makes", "me", "happy"], ["I", "am", "happy"]]
    
    rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob = trainNaiveBayes(rational_dict, emotional_dict, "tweet")
    result = testNaiveBayes(rational_prob, emotional_prob, rational_cond_prob, emotional_cond_prob, rational_absent_cond_prob, emotional_absent_cond_prob, "tweet", test)
    print result
                    
main()