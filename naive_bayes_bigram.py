import sys
import os
import re
import stemmer
import operator
import math
import pickle


#This file contains two functions which are used to train and test data with naive bayes method.
#The input of train_naiveBayes_bigram has three parameters:
#dic_emotional, dic_rational come from the result of preprocess.py
#level is either "user" or "test"

#The input of test_naiveBayes_bigram constains all output from train_naiveBayes_bigram and another two
#parameters: test_list and level
#level is either "user" or "test"
#test_list is a list of list. test_list contains all words of one user.



def train_naiveBayes_bigram(dic_emotional, dic_rational, level):

	bi_new_dic_emotion = {}

	for ele_user in dic_emotional.keys():
		bi_new_dic_emotion[ele_user] = []
		for ele_list in dic_emotional[ele_user]:
			#print ele_list
			if(len(ele_list) == 0):
				continue
			elif(len(ele_list) == 1):
				bi_new_dic_emotion[ele_user].append(ele_list[0])
			else:
				for i in range(0,len(ele_list)-1):
					bi_new_dic_emotion[ele_user].append(ele_list[i] + " " + ele_list[i+1])



	bi_new_dic_ration = {}

	for ele_user in dic_rational.keys():
		bi_new_dic_ration[ele_user] = []
		for ele_list in dic_rational[ele_user]:
			if(len(ele_list) == 0):
				continue
			elif(len(ele_list) == 1):
				bi_new_dic_ration[ele_user].append(ele_list[0])
			else:
				for i in range(0,len(ele_list)-1):
					bi_new_dic_ration[ele_user].append(ele_list[i] + " " + ele_list[i+1])


	num_word_occur_emotion = {}
	num_word_occur_ration = {}

	my_list_emotion = []
	my_list_ration = []
	for ele_user in bi_new_dic_emotion.keys():
		my_list_emotion = my_list_emotion + bi_new_dic_emotion[ele_user]

	for ele_user in bi_new_dic_ration.keys():
		my_list_ration = my_list_ration + bi_new_dic_ration[ele_user]


	#step = 0
	for element in my_list_emotion:
		#step = step + 1
		#print step
		num_word_occur_emotion[element] = num_word_occur_emotion.get(element, 0) + 1
		# if element not in num_word_occur_emotion.keys():
		# 	#print element
		# 	num_word_occur_emotion[element] = my_list_emotion.count(element)

	#step = 0
	for element in my_list_ration:
		#step = step + 1
		#print step
		num_word_occur_ration[element] = num_word_occur_ration.get(element, 0) + 1
		# if element not in num_word_occur_ration.keys():
		# 	num_word_occur_ration[element] = my_list_ration.count(element)


	num_total_words_emotion = len(my_list_emotion)
	num_total_words_ration = len(my_list_ration)
	print num_total_words_emotion, num_total_words_ration
	set_emotion = set()
	set_ration = set()

	for ele in my_list_emotion:
		set_emotion.add(ele)
	for ele in my_list_ration:
		set_ration.add(ele)

	vocabulary = len(set_emotion) + len(set_ration)

	# print vocabulary

	if(level == "user"):
		P_emotion = float(len(bi_new_dic_emotion.keys())) / float(len(bi_new_dic_emotion.keys()) + len(bi_new_dic_ration.keys()))
		P_ration = 1.0 - P_emotion
	elif(level == "tweet"):
		num_emotion = 0
		num_ration = 0
		for ele_user in dic_emotional.keys():
			num_emotion = num_emotion + len(dic_emotional[ele_user])
		for ele_user in dic_rational.keys():
			num_ration = num_ration + len(dic_rational[ele_user])
		P_emotion = float(num_emotion) / float(num_emotion + num_ration)
		P_ration = 1.0 - P_emotion
	else:
		print "Wrong level name, please try again"
	# print P_emotion
	# print P_ration

	return (num_word_occur_emotion, num_word_occur_ration, num_total_words_emotion, num_total_words_ration, vocabulary, P_emotion, P_ration)


def test_naiveBayes_bigram(test_list, num_word_occur_emotion, num_word_occur_ration, num_total_words_emotion, num_total_words_ration, vocabulary, P_emotion, P_ration, level):
	# dic_p_emotion = {}
	# dic_p_ration = {}
	# for ele_user in num_word_occur_emotion.keys():
	# 	dic_p_emotion[ele_user] = math.log10((float(num_word_occur_emotion.get(ele_user, 0) + 1)) / float(int(num_total_words_emotion) + int(vocabulary)))

	# for ele_user in num_word_occur_ration.keys():
	# 	dic_p_ration[ele_user] = math.log10((float(num_word_occur_ration.get(ele_user, 0) + 1)) / float(int(num_total_words_ration) + int(vocabulary)))

	if (level == "user"):
		my_list = []
		for ele_list in test_list:
			if(len(ele_list) == 0):
				continue
			elif(len(ele_list) == 1):
				my_list.append(ele_list[0])
			else:
				for i in range(0,len(ele_list)-1):
					my_list.append(ele_list[i] + " " + ele_list[i+1])
		# print my_list
		P_total_emotion = math.log10(float(P_emotion))
		P_total_ration = math.log10(float(P_ration))
		for ele in my_list:
			P_total_emotion = P_total_emotion + math.log10((float(num_word_occur_emotion.get(ele, 0) + 1)) / float(int(num_total_words_emotion) + int(vocabulary)))
			P_total_ration = P_total_ration + math.log10((float(num_word_occur_ration.get(ele, 0) + 1)) / float(int(num_total_words_ration) + int(vocabulary)))
		if(P_total_emotion > P_total_ration):
			thinking_mode = "emotional thinking"

		else:
			thinking_mode = "rational thinking"

		return thinking_mode

	elif (level == "tweet"):
		P_final_emotion = 0.0
		P_final_ration = 0.0
		for ele_list in test_list:
			my_list = []
			if(len(ele_list) == 0):
				continue
			elif(len(ele_list) == 1):
				my_list.append(ele_list[0])
			else:
				for i in range(0,len(ele_list)-1):
					my_list.append(ele_list[i] + " " + ele_list[i+1])
			P_total_emotion = math.log10(float(P_emotion))
			P_total_ration = math.log10(float(P_ration))
			for ele in my_list:
				P_total_emotion = P_total_emotion + math.log10((float(num_word_occur_emotion.get(ele, 0) + 1)) / float(int(num_total_words_emotion) + int(vocabulary)))
				P_total_ration = P_total_ration + math.log10((float(num_word_occur_ration.get(ele, 0) + 1)) / float(int(num_total_words_ration) + int(vocabulary)))
			P_final_emotion = P_final_emotion + P_total_emotion
			P_final_ration = P_final_ration + P_total_ration

		if(P_final_emotion > P_final_ration):
			thinking_mode = "emotional thinking"
		else:
			thinking_mode = "rational thinking"
		return thinking_mode
	else:
		thinking_mode = "wrong level input, please try again"
		return thinking_mode



