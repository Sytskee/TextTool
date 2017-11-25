'''
=====================================================================================
Script for the selection and evaluation of a new supervised text classification model
=====================================================================================

This script is part of the supplemental material for the paper "Supervised Text Classification: A Tutorial on Model Selection and Evaluation".
It is a Python script written in Python 3.5.2 on a Windows machine. It can best be viewed using Notepad++, see "README.txt"
for more information on how to run this script and the required libraries and packages.
The path to the dataset, language variable, scoring metrics and parameter values can be adjusted directly in this script.
Information on different settings is given in the commented text (indicated by #).
A full explanation of the text classification pipeline and exhaustive CV Gridsearch can be found in the paper.

The code for the pipeline and the gridsearchCV is partly based on the Scikitlearn example script "grid_search_text_feature_extraction.py"
by O. Grisel, P. Prettenhofer, and M. Blondel. This is open source code published on the Scikitlearn website under the BSD 3-clause license.
Retrieved on 01-08-2016 from: http://scikit-learn.org/0.15/auto_examples/grid_search_text_feature_extraction.html
'''

from pprint import PrettyPrinter
from time import time
from datetime import datetime
import logging
import sys
import os
import csv
import pickle
import traceback

from sklearn.datasets import load_files, fetch_20newsgroups
from sklearn.metrics import classification_report
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import LabelKFold, LeaveOneLabelOut, StratifiedKFold
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.preprocessing import MaxAbsScaler
from sklearn.svm import SVC, LinearSVC
from sklearn.feature_selection import chi2
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from multiprocessing import freeze_support

import nltk
import numpy as np

# Fix for placing helper files in the same folder
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from CustomTokenizer import CustomTokenizer
from SelectAtMostKBest import SelectAtMostKBest

class TextClassifier:
    def __init__(self, language, data_set_path, status_report_queue=None):
        self.language = language
        self.status_report_queue = status_report_queue

        # Display progress logs on stdout
        logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

        if getattr(sys, 'frozen', False):
            # frozen
            current_path = os.path.dirname(sys.executable)
        else:
            # unfrozen
            current_path = os.path.dirname(os.path.realpath(__file__))

        output_path = os.path.join(current_path, 'output', '')

        # Create output directory if it does not exist yet
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        output_file = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + '_0.txt'
        self.full_output_file_path = os.path.join(output_path, output_file)

        #self.groups = []
        self.group_number = -1

        self.report_status('Loading data ...')

        # Only used when 20 Newsgroup test set is defined as input dataset
        if data_set_path == 'fetch_20newsgroups':
            self.data = fetch_20newsgroups(categories=['alt.atheism', 'comp.graphics', 'comp.os.ms-windows.misc', 'comp.sys.ibm.pc.hardware', 'comp.sys.mac.hardware', 'comp.windows.x', 'misc.forsale'],
                                           remove=('headers', 'footers', 'quotes'))      # Use 3 of the 20 Newsgroups categories
        else:
            # Use 'utf-8-sig' for files with BOM
            self.data = load_files(data_set_path, encoding='utf-8')     # The path to and encoding of the input dataset

            #for full_file_path in self.data.filenames:
            '''
            for index in range(0, self.data.filenames.size):
                path, filename = os.path.split(self.data.filenames[index])
                groupName = filename[0:filename.find('_')]
                self.groups.append(groupName)
            '''

        #self.train_test_splitter = LeaveOneLabelOut(self.groups)
        self.train_test_splitter = StratifiedKFold(y=self.data.target, n_folds=5)
        #self.train_test_splitter = LabelKFold(labels=self.groups,  n_folds=5)
        self.development_data_indexes = []
        self.test_data_indexes = []

        for development_indexes, test_indexes in self.train_test_splitter:
            self.development_data_indexes.append(development_indexes)
            self.test_data_indexes.append(test_indexes)

        self.report_status('Data loaded')

    def report_status(self, message):
        if self.status_report_queue is not None:
            self.status_report_queue.put('{} -> {}: {}'.format(datetime.now().strftime('%H:%M:%S'), self.group_number + 1, message))

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    def set_parameters(self, parameters, do_stemming, scoring, result_scorings):
        self.parameters = parameters
        self.do_stemming = do_stemming
        self.scoring = scoring
        self.result_scorings = result_scorings

    def get_groups_counter(self):
        return len(self.train_test_splitter)

    def set_next_group_data(self, group_number):
        self.group_number = group_number
        self.current_output_file_path = self.full_output_file_path.replace('_0.txt', '_' + str(group_number) + '.txt')
        print_file = open(self.current_output_file_path, 'a')

        self.development_data = np.array(self.data.data)[self.development_data_indexes[group_number]]
        self.development_target = np.array(self.data.target)[self.development_data_indexes[group_number]]
        self.development_filenames = np.array(self.data.filenames)[self.development_data_indexes[group_number]]
        #self.development_groups = np.array(self.groups)[self.development_data_indexes[group_number]]

        self.test_data = np.array(self.data.data)[self.test_data_indexes[group_number]]
        self.test_target = np.array(self.data.target)[self.test_data_indexes[group_number]]

        debug_line = "Next group data set. Fold number is %s of %s " % (group_number + 1, self.get_groups_counter())
        self.report_status(debug_line)
        print(debug_line, file=print_file)
        print(file=print_file)

        print_file.close()

    def train_and_predict(self):
        print_file = open(self.current_output_file_path, 'a')

        if not hasattr(self, 'pipeline'):
            debug_line = "No pipeline defined"
            self.report_status(debug_line)
            print(debug_line, file=print_file)
            return

        if not hasattr(self, 'parameters'):
            debug_line = "No parameters defined"
            self.report_status(debug_line)
            print(debug_line, file=print_file)
            return


        self.grid_search = GridSearchCV(self.pipeline,
                                        self.parameters,
                                        n_jobs=-1,
                                        verbose=1,
                                        scoring=self.scoring,
                                        #cv=LabelKFold(labels=self.development_groups, n_folds=5),
                                        cv=StratifiedKFold(y=self.development_target, n_folds=5),
                                        refit=True)

        print("Performing exhaustive grid search to find best parameter combination...", file=print_file)
        print("pipeline elements:", [name for name, _ in self.pipeline.steps], file=print_file)
        print("parameter grid:", file=print_file)
        pp = PrettyPrinter(stream=print_file)
        pp.pprint(self.parameters)
        print(" do_stemming = %r" % self.do_stemming, file=print_file)
        print(" scoring = %s" % self.scoring, file=print_file)

        sys.stdout.flush()

        self.report_status("Starting the grid search, this can take a while ...")

        t0 = time()

        try:
            self.grid_search.fit(self.development_data, self.development_target)
        except:
            print("Unexpected error during fitting:", file=print_file)
            print("--------------------------------------------------", file=print_file)
            print(traceback.format_exc(), file=print_file)
            print("--------------------------------------------------", file=print_file)
            print("Aborting this fold", file=print_file)

            self.report_status("Unexpected error during fitting, see log for details")
            self.report_status("Aborting this fold")

            sys.stdout.flush()
            print_file.close()
            return

        print("done in %0.3fs" % (time() - t0), file=print_file)
        print(file=print_file)

        self.report_status("Grid search finished")

        self.report_status("Pickling model...")

        pickle_file = self.current_output_file_path.replace('.txt', '.pkl')
        with open(pickle_file, 'bw') as file:
            pickle.dump(self.grid_search, file)

        self.report_status("Done pickling model")

        self.report_status("Start writing the output to file, check the output file for the results...")

        print("Best score: %0.3f (%s)" % (self.grid_search.best_score_, self.scoring), file=print_file)
        print("Best estimator: %s" % self.grid_search.best_estimator_, file=print_file)
        print("Best parameter set:", file=print_file)
        best_parameters = self.grid_search.best_estimator_.get_params()
        for param_name in sorted(self.parameters.keys()):
            print("\t%s: %r" % (param_name, best_parameters[param_name]), file=print_file)
        print(file=print_file)
        print(file=print_file)


        print("Grid scores on development set:", file=print_file)
        print(file=print_file)
        for params, mean_score, scores in self.grid_search.grid_scores_:
            print("%0.3f (+/-%0.03f) for %r" % (mean_score, scores.std() * 2, params), file=print_file)

        sys.stdout.flush()

        print(file=print_file)
        print(file=print_file)
        print("Per class classification report for the final classifier:", file=print_file)
        print(file=print_file)
        print("The final model is trained on the full development set using the selected parameter settings found by GridSearchCV.", file=print_file)
        print("The scores for the final model are computed on the full test set.", file=print_file)
        print(file=print_file)
        y_pred = self.grid_search.predict(self.test_data)
        print(classification_report(self.test_target, y_pred, target_names=self.data.target_names), file=print_file)
        print(file=print_file)
        print(file=print_file)


        if self.data.target.max() + 1 <= 2:
            # Print the performance score of the final model:
            # For binary classification use:
            print("Performance metrics final model on test set:", file=print_file)
            print("Accuracy:", metrics.accuracy_score(self.test_target, y_pred), file=print_file)
            print("Recall:", metrics.recall_score(self.test_target, y_pred), file=print_file)
            print("Precision:", metrics.precision_score(self.test_target, y_pred), file=print_file)
            print("F1:", metrics.f1_score(self.test_target, y_pred), file=print_file)
            print(file=print_file)
            print(file=print_file)
        else:
            # For multiclass classification use:
            print("Performance metrics final model on test data:", file=print_file)
            print("Accuracy:", metrics.accuracy_score(self.test_target, y_pred), file=print_file)
            print("Weighted Recall:", metrics.recall_score(self.test_target, y_pred, average='weighted', pos_label=None), file=print_file)              # Or average='micro' / average='macro'
            print("Weighted Precision:", metrics.precision_score(self.test_target, y_pred, average='weighted', pos_label=None), file=print_file)        # Or average='micro' / average='macro'
            print("Weighted F1:", metrics.f1_score(self.test_target, y_pred, average='weighted', pos_label=None), file=print_file)                      # Or average='micro' / average='macro'
            print(file=print_file)
            print(file=print_file)

        # Define the number of features to print in the output:
        print_n = 50
        print('Top %d keywords' % (print_n), file=print_file)
        #self.print_most_informative(self.development_data, self.development_target, self.development_filenames, self.data.target_names, print_n)
        self.print_most_informative_new(self.development_data, self.development_target, self.development_filenames,
                                    self.data.target_names, print_file, print_n)
        print(file=print_file)
        print(file=print_file)

        # Print the confusion matrix for the final model:
        cm = confusion_matrix(self.test_target, y_pred)
        np.set_printoptions(precision=2)
        print('Confusion matrix final model', file=print_file)
        print(cm, file=print_file)
        print(file=print_file)

        sys.stdout.flush()
        print_file.close()

    def print_most_informative(self, X, y, filenames, categories, print_file, n):
        vectorizer = self.grid_search.best_estimator_.named_steps['union'].transformer_list[0][1].named_steps['vect']
        tfidf = self.grid_search.best_estimator_.named_steps['union'].transformer_list[0][1].named_steps['tfidf']
        chi2 = self.grid_search.best_estimator_.named_steps['chi2']

        vectorizer_fit = vectorizer.fit_transform([text['text'] for text in X])
        tfidf_fit = tfidf.fit_transform(vectorizer_fit)
        chi2.fit(tfidf_fit, y)

        chi2_values = chi2.scores_.tolist()
        p_values = chi2.pvalues_.tolist()

        X_array = vectorizer_fit.toarray()
        feature_names = vectorizer.get_feature_names()

        sorted_chi2_values = sorted(chi2_values)

        header_line = '%25s  |  %6s  |  %5s' % ('feature name', 'CHI2', 'P')

        for category in categories:
            header_line += '  |  %6s' % (category)

        print(header_line, file=print_file)
        print('%s' % ('-' * len(header_line)), file=print_file)

        i = 0

        while(True):
            value_to_search = sorted_chi2_values[len(sorted_chi2_values)-1-i]
            feature_indexes = [i for i, x in enumerate(chi2_values) if x == value_to_search]

            for feature_index in feature_indexes:
                count = {}

                for category in categories:
                    count[category] = {}

                for id_for_file, words_in_file in enumerate(X_array):
                    for category in categories:
                        if category in filenames[id_for_file]:
                            if feature_names[feature_index] in count[category]:
                                count[category][feature_names[feature_index]] += words_in_file[feature_index]
                            else:
                                count[category][feature_names[feature_index]] = words_in_file[feature_index]

                row = '%25s  |  %2.4f  |  %1.3f' % (feature_names[feature_index], chi2_values[feature_index], p_values[feature_index])

                for category in categories:
                    if feature_names[feature_index] in count[category]:
                        temp_count = count[category][feature_names[feature_index]]
                    else:
                        temp_count = 0

                    row += '  |  %6d' % (temp_count)

                print(row, file=print_file)
                i += 1
                sys.stdout.flush()

            if i >= n:
                break

        print(file=print_file)

    def print_most_informative_new(self, X, y, filenames, categories, print_file, n):
        # Gathering data
        mean_feature_values = {}
        category_value_count = {}

        for category in categories:
            mean_feature_values[category] = {}
            category_value_count[category] = {}

        text_step = self.grid_search.best_estimator_.named_steps['text']
        text_step_result = text_step.fit_transform(X, y)

        chi2 = self.grid_search.best_estimator_.named_steps['chi2']
        chi2.fit(text_step_result, y)

        # selector = self.grid_search.best_estimator_.named_steps['union'].transformer_list[0][1].named_steps['selector']
        # selector_result = selector.fit_transform(extractTextAndFeatures_result, y)

        text_vectorizer = self.grid_search.best_estimator_.named_steps['text'].named_steps['vect']
        text_vectorizer_result = text_vectorizer.fit_transform(X, y)

        feature_names = []
        feature_names.extend(['text' + '__' + f for f in text_vectorizer.get_feature_names()])

        union_result_array = text_step_result.toarray()

        sorted_chi2_values = np.sort(chi2.scores_)[::-1] # sort and reverse
        sorted_chi2_values = sorted_chi2_values[np.logical_not(np.isnan(sorted_chi2_values))] # remove nan values

        # Printing
        header_line = '%25s  |  %6s  |  %5s' % ('feature name', 'CHI2', 'P')

        for category in categories:
            header_line += '  |  %9s' % (category)

        print(header_line, file=print_file)
        print('%s' % ('-' * len(header_line)), file=print_file)

        i = 0
        while i < sorted_chi2_values.__len__() and i < n:
            value_to_search = sorted_chi2_values[i]
            feature_indexes = [i for i, x in enumerate(chi2.scores_) if x == value_to_search]

            if feature_indexes.__len__ == 0:
                print("No feature indexes found for value '" + value_to_search + "', trying the next one", file=print_file)
                i += 1

            if value_to_search ==  float('nan'):
                print("Value to search is 'nan', trying the next one", file=print_file)
                i += 1

            for feature_index in feature_indexes:
                count = {}

                for category in categories:
                    count[category] = {}

                for id_in_development_set, words_in_file in enumerate(union_result_array):
                    category = categories[y[id_in_development_set]]

                    if feature_names[feature_index].startswith('text__'):
                        if feature_names[feature_index] in count[category]:
                            count[category][feature_names[feature_index]] += text_vectorizer_result[id_in_development_set, feature_index]
                        else:
                            count[category][feature_names[feature_index]] = text_vectorizer_result[id_in_development_set, feature_index]
                    else:
                        count[category][feature_names[feature_index]] = mean_feature_values[category][feature_names[feature_index].replace('file__', '')]


                row = '%25s  |  %2.4f  |  %1.3f' % (feature_names[feature_index], chi2.scores_[feature_index], chi2.pvalues_[feature_index])

                for category in categories:
                    if feature_names[feature_index] in count[category]:
                        temp_count = count[category][feature_names[feature_index]]
                    else:
                        temp_count = 0

                    if feature_names[feature_index].startswith('text__'):
                        row += '  |  %9d' % (temp_count)
                    else:
                        row += '  |  %9.2f' % (temp_count)

                print(row, file=print_file)
                i += 1

                if i >= n:
                    break

        print(file=print_file)



########################################################################################################################
########################################################################################################################
########################################################################################################################

# Definition Text classification pipeline and Parameter Grid
def pipeline_and_parameters(text_classifier, search_scoring, result_scorings, file_names, cvs_files_path):
    text_classifier.set_pipeline(Pipeline([
        ('text', Pipeline([
            ('vect', CountVectorizer(tokenizer=CustomTokenizer(text_classifier.language, True), lowercase=True, strip_accents='unicode', analyzer='word')),
            ('tfidf', TfidfTransformer()),
        ])),

        ('chi2', SelectAtMostKBest(chi2)),
        ('clf', LinearSVC()),     # Or ('clf', SVC(kernel='linear')),
    ]))

    chi__k = list(range(10, 501, 20))                                                                        # Set parameter range + step size for Select K best features
    chi__k.append('all')

    text_classifier.set_parameters({
        'text__vect__min_df': [1, 2, 3],                                                              # Number of training documents a term should occur in
        'text__vect__ngram_range': [(1, 1), (2, 2), (3, 3), (1, 3)],                                  # Test uni-, bi-, tri-, or N-multigrams ranging from 1-3
        'text__vect__stop_words': [nltk.corpus.stopwords.words(text_classifier.language), None],      # Do/do not remove stopwords
        'text__tfidf__use_idf': [True, False],                                                        # Weight terms by tf or tfidf
        'chi2__k': chi__k,                                                                                   # Select K most informative features
        'clf__C': [1, 2, 3, 10, 100, 1000],                                                                  # Compare different values for C parameter
        'clf__class_weight': ['balanced'],                                                                   # Weighted vs non-weighted classes
    }, do_stemming=True, scoring=search_scoring, result_scorings=result_scorings)                            # Stem keywords

def pipeline_and_parameters2(text_classifier, search_scoring, result_scorings, file_names, cvs_files_path):
    text_classifier.set_pipeline(Pipeline([
        ('text', Pipeline([
            ('vect', CountVectorizer(tokenizer=CustomTokenizer(text_classifier.language, True), lowercase=True,
                                     strip_accents='unicode', analyzer='word')),
            ('tfidf', TfidfTransformer()),
        ])),

        ('chi2', SelectAtMostKBest(chi2)),
        ('clf', SVC(kernel='linear')),  # Or ('clf', LinearSVC()),
    ]))

    chi__k = list(range(10, 10, 20))  # Set parameter range + step size for Select K best features
    chi__k.append('all')

    text_classifier.set_parameters({
        'text__vect__min_df': [1],  # Number of training documents a term should occur in
        'text__vect__ngram_range': [(1, 1)], # Test uni-, bi-, tri-, or N-multigrams ranging from 1-3
        'text__vect__stop_words': [None], # Do/do not remove stopwords
        'text__tfidf__use_idf': [False],  # Weight terms by tf or tfidf
        'chi2__k': chi__k,  # Select K most informative features
        'clf__C': [1],  # Compare different values for C parameter
        'clf__class_weight': [None],  # Weighted vs non-weighted classes
    }, do_stemming=True, scoring=search_scoring, result_scorings=result_scorings)  # Stem keywords

# if __name__ == "__main__":
#     freeze_support()
#
#     # Set variable to language of dataset, e.g. 'dutch', 'english' or any other language supported by NLTK
#     language = 'dutch'
#
#     # Set path to Main folder with dataset on your computer that contains the categorized subfolders (see README file for more information).
#     # To test the script on the 20 Newsgroups dataset, use: file_path = 'fetch_20newsgroups'
#     file_path = r'C:\Users\Sytske\Desktop\InterapyTestJoost'
#     #file_path = 'fetch_20newsgroups'
#
#     # Create the classifier with the language and dataset:
#     text_classifier = TextClassifier(language, file_path)
#
#     print_file = open(text_classifier.full_output_file_path, 'w')
#     # print("%d documents (%d development, %d test)" % (len(self.data.filenames), len(self.development_data), len(self.test_data)))
#     print("%d documents" % len(text_classifier.data.filenames), file=print_file)
#     print("%d categories" % len(text_classifier.data.target_names), file=print_file)
#     print("%d groups" % len(text_classifier.train_test_splitter), file=print_file)
#     print(text_classifier.train_test_splitter, file=print_file)
#     print(file=print_file)
#
#     if os.path.isdir(file_path):
#         dirs = [os.path.join(file_path, o) for o in os.listdir(file_path) if
#                 os.path.isdir(os.path.join(file_path, o))]
#         number_of_classes = dirs.__len__()
#     else:
#         number_of_classes = -1
#
#     number_of_groups = text_classifier.get_groups_counter()
#
#     for i in range(number_of_groups):
#         text_classifier.set_next_group_data(i)
#
#         if number_of_classes == 2:
#             # For binary classifiers: ['accuracy', 'precision', 'recall', 'f1']
#             scorings = ['f1']
#         else:
#             # For multiclass classifiers: ['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'] or
#             #                             ['accuracy', 'precision_micro', 'recall_micro', 'f1_micro'] or
#             #                             ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
#             scorings = ['f1_weighted']
#
#
#         # Apply pipeline and parameters:
#         for scoring in scorings:
#             pipeline_and_parameters(text_classifier, scoring, [result_scoring for result_scoring in scorings if result_scoring is not scoring], text_classifier.development_filenames, file_path)
#             text_classifier.train_and_predict()
#
#
# ########################################################################################################################
# ########################################################################################################################
# ########################################################################################################################