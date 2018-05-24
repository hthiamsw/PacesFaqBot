import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_predict
import pandas as pd
import pickle
import pdb
from sklearn import metrics
from sklearn.linear_model import SGDClassifier
from sklearn.utils import class_weight
from sklearn.linear_model import PassiveAggressiveClassifier


def read_data():
    """ Return a df of data

    Read all data and return a df
    """
    df = pd.DataFrame(columns=['QA', 'label'])
    for dirpath, dirs, files in os.walk('./data/corpus/'):
        for file_name in files:
            if file_name.endswith('.json'):
                fileName = os.path.splitext(os.path.splitext(file_name)[0])[0]  # for labeling of dataset
                data = pd.read_json(dirpath + "/" + file_name, orient='values')
                i = 0
                print(file_name + "'s datas added")
                while i < len(data):
                    '''
                    William - 20180524
                    Replaced as unicode is replaced with str and str with bytes in Python 3
                    if isinstance(data["Question"][i], unicode) or isinstance(data["Question"][i], str)
                    '''                
                    if isinstance(data["Question"][i], bytes) or isinstance(data["Question"][i], str):
                        datas = pd.DataFrame(
                            {'QA': [data["Question"][i]], 'label': fileName})  # 1 ANSWER and classification DF
                        df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                    else:
                        for entries in data["Question"][i]:
                            datas = pd.DataFrame(
                                {'QA': [entries], 'label': fileName})  # multiple ANSWERS and classification DF
                            df = pd.concat([df, datas], ignore_index=True)
                    if isinstance(data["Answer"][i], bytes) or isinstance(data["Answer"][i], str):
                        datas = pd.DataFrame(
                            {'QA': [data["Answer"][i]], 'label': fileName})  # 1 ANSWER and classification DF
                        df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                    else:
                        for entries in data["Answer"][i]:
                            datas = pd.DataFrame(
                                {'QA': [entries], 'label': fileName})  # multiple ANSWERS and classification DF
                            df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                    i += 1
            elif file_name.endswith('.csv'):
                print(file_name + "'s datas added")
                with open('./data/corpus/' + file_name, 'r') as csvfile:
                    data = csvfile.readlines()
                    data = data[0].split(',')
                    csvfile.close()
                fileName = os.path.splitext(os.path.splitext(file_name)[0])[0]  # for labeling of dataset
                i = 0
                while i < len(data):
                    datas = pd.DataFrame({'QA': [data[i]],
                                          'label': [fileName]})  # data and classification DF
                    df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                    i += 1;
                    '''
                    if i == len(data) - 1:
                        datas = pd.DataFrame({'QA': [data[i].decode('utf-8', 'ignore')],
                                              'label': [fileName]})  # data and classification DF
                        df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                        i += 1
                    else:
                        datas = pd.DataFrame({'QA': [data[i].decode('utf-8', 'ignore')],
                                              'label': [fileName]})  # data and classification DF
                        df = pd.concat([df, datas], ignore_index=True)  # appending to pandas dataframe
                        i += 1
                    '''
        return df


def compute_class_weight(df):
    """ Return a dict of class weight

    Compute the different class weight according to number of data in df
    """
    weight = class_weight.compute_class_weight('balanced', np.unique(df.label), df.label)
    class_dict = {}
    for labels, weight in zip(np.unique(df.label), weight):
        class_dict[labels] = weight
    print(class_dict)
    return class_dict


def create_pipeline(class_weight):
    """ Return a pipeline

   Create a pipeline that vectorize the corpus before going through a classifier
   """
    text_clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 1), stop_words='english', use_idf=True, encoding='word'),
                             # Creation of pipeline to train
                             SGDClassifier(loss='hinge', penalty='l2',
                                           alpha=0.001, n_iter=5,
                                           class_weight=class_weight),
                             # PassiveAggressiveClassifier(class_weight = class_dict), #56%
                             )
    return text_clf


def fit_predict(text_clf, df):
    """ Return a classifier

    fits the data to the pipeline and calculate the prediction accuracy
    """
    _clf = text_clf.fit(df['QA'], df['label'])  # Use when deployment
    cross_predict = cross_val_predict(text_clf, df.QA, df.label, cv=15)
    print("Accuracy :" + str(metrics.accuracy_score(df.label, cross_predict)))  # accuracy
    return _clf


def write_pickle(clf):
    """ Return none

    Saves the classifier to persistent data to be used by chatbot
    """
    save_clf = open("text_clf.pickle", "wb")  # Saving the classifier to a pickle file
    pickle.dump(clf, save_clf)
    save_clf.close()
    print("Wrote to pickle file successfully.")


def retrain_clf(question, classification):
    """ Return none

    Admin invoking the retraining of classifier
    """
    classfier_f = open("text_clf.pickle", "rb")  # Setting up connection to saved classifier pickle file
    text_clf = pickle.load(classfier_f)  # loading classifier to a local variable
    classfier_f.close()
    if text_clf.predict([question])[0] == classification:
        return 'ok'
    df = read_data()
    class_weight = compute_class_weight(df)
    text_clf = create_pipeline(class_weight)
    text_clf = fit_predict(text_clf, df)
    write_pickle(text_clf)


def retrain_partial_clf(classification, question, answer, alternative, quality):
    """ Return none
    //TO BE IMPLEMENTED********************************
    Admin invoking the retraining of classifier
    Does a partial fit
    """
    classifier_f = open("text_clf.pickle", "rb")  # Setting up connection to saved classifier pickle file
    text_clf = pickle.load(classifier_f)  # loading classifier to a local variable

    classifier_f.close()
    if text_clf.predict([question])[0] == classification:
        return 'ok'
    dd = {i: v for i, v in enumerate([2, 1.5, 1.2, 1.1, 1], 1)}
    weight = dd[int(quality)]
    sample_weight = []
    partial_df = pd.DataFrame(columns=['QA', 'label'])
    datas = pd.DataFrame({'QA': [question], 'label': classification})  # 1 ANSWER and classification DF
    partial_df = pd.concat([partial_df, datas], ignore_index=True)
    sample_weight.append(weight)
    for ans in answer:
        datas = pd.DataFrame({'QA': [ans], 'label': classification})
        partial_df = pd.concat([partial_df, datas], ignore_index=True)
        sample_weight.append(weight)
    for alt in alternative:
        datas = pd.DataFrame({'QA': [alt], 'label': classification})
        partial_df = pd.concat([partial_df, datas], ignore_index=True)
        sample_weight.append(weight)

    vect = text_clf.steps[0][1]
    data_list = vect.transform(partial_df.QA)

    text_clf.steps[1][1].partial_fit(data_list, partial_df.label, sample_weight=sample_weight)

    save_clf = open("text_clf.pickle", "wb")  # Saving the classifier to a pickle file
    pickle.dump(text_clf, save_clf)
    save_clf.close()
    print("SUCCESS : Wrote to pickle file")
    

if __name__ == "__main__":
    """ Return none

    Invoking the training of classifier manually
    """
    df = read_data()
    class_weight = compute_class_weight(df)
    text_clf = create_pipeline(class_weight)
    text_clf = fit_predict(text_clf, df)
    write_pickle(text_clf)
