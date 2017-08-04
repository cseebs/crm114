#!/usr/bin/env python
from __future__ import print_function
import os, re
from operator import itemgetter
from crm114 import Classifier
from math import floor

"""
Performs an extremely basic set of tests by passing some fuzzily-defined words
and phrases to the learner with an explicit sentiment, and runs an equally
fuzzy and arbitrary set of texts through the classifier.

Hopefully it gets them right.
"""


if __name__ == '__main__':
    #data_path = '%s%s%s' % (os.path.dirname(__file__), os.sep, 'data')
    data_path = 'data'
    categories = ['nonspam', 'spam']
    #data = ['sls/amazon_cells_labelled.txt', 'sls/imdb_labelled.txt', 'sls/yelp_labelled.txt']
    
    print('Initializing classifier')
    print('- Categories:  %s' % ', '.join(categories))
    print('- Data path:   %s' % data_path)

    c = Classifier(data_path, categories)
    for file_path in c.file_list():
        if os.path.exists(file_path):
            os.remove(file_path)

        print('- Data file:   %s' % file_path)

    c.create_files()
    print('')

    classify_texts = []
    classify_actual = []

    direcs = ["deleted_items", "discussion_threads"]

    regex = re.compile("Demand Ken Lay Donate Proceeds from Enron Stock Sales")
    match = 0

    file_names = []
        
    for i in range (0,2):
        for myfile in os.listdir("/home/pi/enron/lay-k/%s/" % direcs[i]):
            with open("/home/pi/enron/lay-k/%s/%s" \
                      % (direcs[i],myfile), 'r') as f:
                string = f.read()
                classify_texts.append(string)
                file_names.append("%s/%s" % (direcs[i], myfile))

                found = regex.search(string)
                if found != None:
                    match += 1
                    classify_actual.append('spam')
                    c.learn('spam', string)
                else:
                    classify_actual.append('nonspam')
                    #c.learn('nonspam', string)
                
    print('total matches: %d\n' % match)

    train_string = 'Demand Ken Lay Donate Proceeds from Enron Stock Sales'
    
    c.learn('spam', train_string)
    c.learn('spam', train_string)
    c.learn('spam', train_string.lower())
    c.learn('nonspam', 'Everything else is nonspam')
    c.learn('nonspam', 'if it doesnt have it, its nonspam.')
    c.learn('nonspam', 'must have it to be spam')
    c.learn('nonspam', 'an ordinary email isnt spam')
    c.learn('nonspam', 'dont count normal messages')
    c.learn('nonspam', 'seriously, dont do it')
        

    category_max = len(max(categories, key=len))
    test_output_format = '%% 3.2f%%%%  %%%ds:  %%s' % category_max

    test_results = []

    spam_count = 0
    total_count = 0
    classified_incorrect = []
    count=0
    
    for text in classify_texts:
        category, probability = c.classify(text)
        test_results.append({'category': category,
                         'probability': probability,
                         'text': file_names[total_count]})
        
        if int(floor(probability*100)) < 90:
            category = 'nonspam'
            count+=1

        if category == 'spam':
            spam_count += 1

        if category != classify_actual[total_count]:
            classified_incorrect.append(file_names[total_count])
            #c.learn(classify_actual[total_count],text)
                                        
        total_count += 1

        if total_count % 100 == 0:
            print(total_count)


    sorted_results = sorted(test_results, key=itemgetter('probability'),
                            reverse=True)
    
    for test in sorted_results:
        print(test_output_format % (test['probability'] * 100.0,
                                    test['category'],
                                    test['text']))
    
    print('spam count: %d / %d = %.2f%%\n' % (spam_count, total_count,
                                              float(spam_count) / total_count * 100))

    print(classified_incorrect)
    print(count)
