from pymongo import MongoClient
import pickle
import pdb
import random
from fuzzywuzzy import fuzz
import pandas as pd
import json
from gensim.models import KeyedVectors
from scipy import spatial
import math
import unicodedata
import sys
import csv

client = MongoClient()
db = client.test  # Database used
qa_Col = db.QA  # Collections for hardcoded Questions Answers

clf_pickle = open("text_clf.pickle", "rb")  # Setting up connection to saved classifier pickle file
text_clf = pickle.load(clf_pickle)  # loading classifier to a local variable
clf_pickle.close()

rec_pickle = open("recommend.pickle", "rb")  # Setting up connection to saved classifier pickle file
recommend_clf = pickle.load(rec_pickle)  # loading classifier to a local variable
rec_pickle.close()

# model = 0
# Loading the pre-trained word2vec google news model
model = KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin.gz', binary=True)

tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                    if unicodedata.category(unichr(i)).startswith('P'))


def retrieve_response(entry):
    """ Return a dict of class weight

     Compute the different class weight according to number of data in df
     """
    entry = entry.lower()
    print entry
    if not (qa_Col.find_one({'Question': entry.lower()}) is None):  # HARDCODED QA
        return qa_Col.find_one({'Question': entry.lower()})['Answer']
    else:
        entry = entry.translate(tbl)
        classification = classify_response(entry)
        # DEPRECIATED: Connect to classification db. currently using json file instead
        # clf_Col = db[classification]
        # cur = clf_Col.find()
        # if cur.count()==0:
        #     return 'Predicted: ' + classification + ' Classification.\n Unable to retrieve response as no collection'
        # return 'Predicted: ' + classification + ' Classification.\n' + get_Response_db(cur, entry)
        if not classification == "recommend":
            response, score = get_response_json(classification, entry)
            if score > 0.5:
                return 'Predicted: ' + classification + ' Classification. ' + response
            else:
                return response, False
        else:
            flag = False
            with open('./data/High_areas.csv', 'rt') as f:
                reader = csv.reader(f, delimiter=',')
                for areas in reader:
                    for area in areas:
                        if area in entry:
                            flag = True
            if flag:
                return 'In which domain are you looking at?\n(e.g text/video analysis)'
            expert = classify_recommendation(entry)
            contact = {}
            email = ''
            with open('./data/Contact_List.csv', 'r') as csvfile:
                data = csvfile.readlines()[1:]
            for person in data:
                person = person.split(',')
                contact[person[0]] = person[-1].split('\r')[0]
            for person in contact:
                if fuzz.partial_token_sort_ratio(person, expert) > 80:
                    email = contact[person]
            return 'Predicted: Recommend Classification.\n You can go to ' + expert + '! :) ' + \
                   'He can be contacted at: ' + email


def classify_response(entry):
    """ Return a classification of the user's input

    """
    global text_clf
    return text_clf.predict([entry])[0]


def classify_recommendation(entry):
    """ Return an expert according to the the user's input if recommend classification

    """
    global recommend_clf
    return recommend_clf.predict([entry])[0]


def get_response_db(cur, entry):
    """ Return a response

    DEPRECIATED: USING JSON FILE FOR THE RESPONSE MATCHING INSTEAD

    """
    max_ = 0
    random_no = random.randint(0, cur.count() - 1)
    if isinstance(cur[random_no], unicode) or isinstance(cur[random_no], str):  # random answer if none for metrics
        response_ = cur[random_no]["Answer"]
    else:
        response_ = random.choice(cur[random_no]["Answer"])
    for qns in cur:
        metrics = fuzz.ratio(qns["Question"], entry)  # Retrieving
        if metrics > max_:
            max_ = metrics
            response_ = qns["Answer"]
    if isinstance(response_, unicode) or isinstance(response_, str):
        return response_
    else:
        return random.choice(response_)


def get_response_json(classification, entry):
    """ Return a response from the classification's json QA corpus

    Use fuzzywuzzy if word2vec model is absent

    Else use word2vec
    """
    max_ = 0
    data = pd.read_json('./data/corpus/' + classification.lower() + '.json', orient='index')
    if model == 0:
        return match_fuzzywuzzy(data, entry, max_)
    else:
        return match_word2vec(data, entry, max_)


def match_word2vec(data, entry, max_):
    """" USING word2vec

    Find average vector of user input and QA copurs Question
    Find highest score
    return highest score if > threshold

    if only 1 word and not in model, fall back to fuzzy wuzzy
    else skip that word
    """
    fuzz_flag = False
    entry = entry.split()
    i = 0.0
    query_meaning = 0
    for words in entry:
        try:
            query_meaning += model[words]
        except KeyError:
            continue
        i += 1
    try:
        query_meaning = query_meaning / i
    except ZeroDivisionError:
        query_meaning = 0
    i = 0.0
    for pair in data:
        for qns in data[pair]["Question"]:
            question_meaning = 0.0
            words = qns.split()
            for word in words:
                try:
                    question_meaning += model[word]
                except KeyError:
                    continue
                i += 1
            try:
                question_meaning = question_meaning / i
            except ZeroDivisionError:
                query_meaning = 0
            try:
                score = 1 - spatial.distance.cosine(query_meaning, question_meaning)
            except ValueError:
                score = 0
            if math.isnan(score):
                print "FAILED: query/question not in model dict"
                fuzz_flag = True
                score = 0
            if score >= max_:
                max_ = score
                response_ = data[pair]["Answer"]
                closest_match = qns
    print 'COSINE SIMILARITY: ' + str(max_)
    if max_ > 0.5:
        return random.choice(response_), max_
    elif fuzz_flag:
        # FUZZY WUZZY HERE
        max_ = 0
        entry = ' '.join(entry)
        for pair in data:
            for qns in data[pair]["Question"]:
                metrics = fuzz.ratio(qns, entry)  # Retrieving
                if metrics > max_:
                    max_ = metrics
                    max_ = max_ / 100.0
                    response_ = data[pair]["Answer"]
                    closest_match = qns
        print 'FUZZY WUZZY SIMILARITY: ' + str(max_)
        if max_ > 0.5:
            return random.choice(response_), 'test'
    return closest_match, max_
    # word2vec ENDS HERE----------------------------------


def match_fuzzywuzzy(data, entry, max_):
    """ USING FUZZYWUZZY

    """
    for pair in data:
        if isinstance(data[pair]["Question"], unicode) or isinstance(data[pair]["Question"],
                                                                     str):  # if question is not an array
            metrics = fuzz.ratio(data[pair]["Question"], entry)  # Retrieving
            if metrics > max_:
                max_ = metrics
                response_ = data[pair]["Answer"]
        else:
            for qns in data[pair]["Question"]:
                metrics = fuzz.ratio(qns, entry)  # Retrieving
                if metrics > max_:
                    max_ = metrics
                    response_ = data[pair]["Answer"]
    if isinstance(response_, unicode) or isinstance(response_, str):
        return response_
    else:
        return random.choice(response_), 'test'


def get_confirmed_response_json(classification, entry):
    """ Return a confirmed response after user's confirmation of question pair

    """
    max_ = 0
    data = pd.read_json('./data/corpus/' + classification.lower() + '.json', orient='index')
    # if model == 0:
    # USING FUZZYWUZZY-------------------------------------------
    for pair in data:
        if isinstance(data[pair]["Question"], unicode) or isinstance(data[pair]["Question"],
                                                                     str):  # if question is not an array
            metrics = fuzz.ratio(data[pair]["Question"], entry)  # Retrieving
            if metrics > max_:
                max_ = metrics
                response_ = data[pair]["Answer"]
        else:
            for qns in data[pair]["Question"]:
                metrics = fuzz.ratio(qns, entry)  # Retrieving
                if metrics > max_:
                    max_ = metrics
                    response_ = data[pair]["Answer"]
    # return 'test asd as', False
    if isinstance(response_, unicode) or isinstance(response_, str):
        return response_
    else:
        return random.choice(response_)


def retrieve_corpus(classification):
    """ Return all answers from corpus

    """
    data = pd.read_json('./data/corpus/' + classification.lower() + '.json', orient='values')
    data = data['Answer']
    result = []
    for item in data:
        result.append(item)
    return result


def update_training_data(classification, question, answer, alternative):
    """ Used to update the json corpus with ground truth from admin

    """
    if not answer and not alternative:  # admin selects classification but no input for corpus and alternative
        return 'OK'
    with open("./data/corpus/" + classification.lower().replace(" ", "") + ".json", "r") as jsonFile:
        data = json.load(jsonFile)
        jsonFile.close
    if not answer and alternative:  # admin selects classification but no input for corpus
        flag = False  # Check if there is a close string match
        for alt in alternative:
            for qa in data:
                for qns in qa['Question']:
                    if fuzz.ratio(qns, question) > 80:  # near match with training data question and entry
                        for ans in qa['Answer']:
                            if fuzz.ratio(ans, alt) > 80:
                                flag = True
                                break
                            if alt is alternative[-1] and fuzz.ratio(qa['Answer'][-1], alt) < 60:
                                flag = True
                                qa['Answer'].append(alt)  # this is the problem
                                break
            if not flag:
                tmp = {u'Answer': alternative, u'Question': [question]}
                data.append(tmp)
        with open("./data/corpus/" + classification.lower().replace(" ", "") + ".json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4, sort_keys=True)
            jsonFile.close
            return 'ok'
    elif answer and not alternative:  # admin selects corpus but no input for
        for ans in answer:
            for qa in data:
                flag = False
                i = 0
                while i < len(qa['Answer']):
                    if fuzz.ratio(qa['Answer'][i], ans) > 80:
                        if fuzz.ratio(question, qa['Question']) > 60:
                            break
                        for qns in qa['Question']:
                            if fuzz.ratio(qns, question) > 80:
                                flag = True
                                break
                        if not flag:
                            qa['Question'].append(question)
                    i += 1
        with open("./data/corpus/" + classification.lower().replace(" ", "") + ".json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4, sort_keys=True)
            jsonFile.close
            return 'ok'
    else:
        for ans in answer:
            for qa in data:
                flag = False
                i = 0
                while i < len(qa['Answer']):
                    if fuzz.ratio(qa['Answer'][i], ans) > 80:
                        if fuzz.ratio(question, qa['Question']) > 60:
                            break
                        for qns in qa['Question']:
                            if fuzz.ratio(qns, question) > 80:
                                flag = True
                                break
                        if not flag:
                            qa['Question'].append(question)
                    i += 1
        for alt in alternative:
            for qa in data:
                for qns in qa['Question']:
                    if fuzz.ratio(qns, question) > 80:  # near match with training data question and entry
                        for ans in qa['Answer']:
                            if fuzz.ratio(ans, alt) > 80:
                                flag = True
                                break
                            if alt is alternative[-1] and fuzz.ratio(qa['Answer'][-1], alt) < 60:
                                flag = True
                                qa['Answer'].append(alt)  # this is the problem
                                break
            if not flag:
                tmp = {u'Answer': alternative, u'Question': [question]}
                data.append(tmp)
        with open("./data/corpus/" + classification.lower().replace(" ", "") + ".json", "w") as jsonFile:
            json.dump(data, jsonFile, indent=4, sort_keys=True)
            jsonFile.close


def update_classifier():  #
    """ used to reopen new classifier generated by train_clf.py

    """
    clf_pickle = open("text_clf.pickle", "rb")  # Setting up connection to saved classifier pickle file
    global text_clf
    text_clf = pickle.load(clf_pickle)  # loading classifier to a local variable
    clf_pickle.close()
    print "SUCCESS : Using new pickle file for chatbot"
