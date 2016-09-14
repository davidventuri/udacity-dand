#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

features_list = [
                 'poi',
                 'salary',
                 # 'deferral_payments',
                 # 'total_payments',
                 # 'loan_advances',
                 'bonus',
                 'bonus_salary_ratio',
                 # 'restricted_stock_deferred',
                 # 'deferred_income',
                 'total_stock_value',
                 # 'expenses',
                 'exercised_stock_options',
                 # 'other',
                 # 'long_term_incentive',
                 # 'restricted_stock',
                 # 'director_fees',
                 # 'to_messages',
                 # 'from_poi_to_this_person',
                 # 'from_poi_to_this_person_percentage',
                 # 'from_messages',
                 # 'from_this_person_to_poi',
                 'from_this_person_to_poi_percentage',
                 'shared_receipt_with_poi'
                 ]

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers

data_dict.pop("TOTAL")
data_dict.pop("THE TRAVEL AGENCY IN THE PARK")

### Task 3: Create new feature(s)

# Bonus-salary ratio
for employee, features in data_dict.iteritems():
	if features['bonus'] == "NaN" or features['salary'] == "NaN":
		features['bonus_salary_ratio'] = "NaN"
	else:
		features['bonus_salary_ratio'] = float(features['bonus']) / float(features['salary'])

# from_this_person_to_poi as a percentage of from_messages
for employee, features in data_dict.iteritems():
	if features['from_this_person_to_poi'] == "NaN" or features['from_messages'] == "NaN":
		features['from_this_person_to_poi_percentage'] = "NaN"
	else:
		features['from_this_person_to_poi_percentage'] = float(features['from_this_person_to_poi']) / float(features['from_messages'])

# from_poi_to_this_person as a percentage of to_messages
for employee, features in data_dict.iteritems():
	if features['from_poi_to_this_person'] == "NaN" or features['to_messages'] == "NaN":
		features['from_poi_to_this_person_percentage'] = "NaN"
	else:
		features['from_poi_to_this_person_percentage'] = float(features['from_poi_to_this_person']) / float(features['to_messages'])

### Impute missing email features to mean
email_features = ['to_messages',
	              'from_poi_to_this_person',
	              'from_poi_to_this_person_percentage',
	              'from_messages',
	              'from_this_person_to_poi',
	              'from_this_person_to_poi_percentage',
	              'shared_receipt_with_poi']
from collections import defaultdict
email_feature_sums = defaultdict(lambda:0)
email_feature_counts = defaultdict(lambda:0)

for employee, features in data_dict.iteritems():
	for ef in email_features:
		if features[ef] != "NaN":
			email_feature_sums[ef] += features[ef]
			email_feature_counts[ef] += 1

email_feature_means = {}
for ef in email_features:
	email_feature_means[ef] = float(email_feature_sums[ef]) / float(email_feature_counts[ef])

for employee, features in data_dict.iteritems():
	for ef in email_features:
		if features[ef] == "NaN":
			features[ef] = email_feature_means[ef]

### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys=True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a variety of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import SelectKBest
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline

# Potential pipeline steps
scaler = MinMaxScaler()
select = SelectKBest()
dtc = DecisionTreeClassifier()
svc = SVC()
knc = KNeighborsClassifier()

# Load pipeline steps into list
steps = [
		 # Preprocessing
         ('min_max_scaler', scaler),
         
         # Feature selection
         ('feature_selection', select),
         
         # Classifier
         ('dtc', dtc)
         # ('svc', svc)
         # ('knc', knc)
         ]

# Create pipeline
pipeline = Pipeline(steps)

# Parameters to try in grid search
parameters = dict(
                  feature_selection__k=[2, 3, 5, 6], 
                  dtc__criterion=['gini', 'entropy'],
                  # dtc__splitter=['best', 'random'],
                  dtc__max_depth=[None, 1, 2, 3, 4],
                  dtc__min_samples_split=[1, 2, 3, 4, 25],
                  # dtc__min_samples_leaf=[1, 2, 3, 4],
                  # dtc__min_weight_fraction_leaf=[0, 0.25, 0.5],
                  dtc__class_weight=[None, 'balanced'],
                  dtc__random_state=[42]
                  # svc__C=[0.1, 1, 10, 100, 1000],
                  # svc__kernel=['rbf'],
                  # svc__gamma=[0.001, 0.0001]
                  # knc__n_neighbors=[1, 2, 3, 4, 5],
                  # knc__leaf_size=[1, 10, 30, 60],
                  # knc__algorithm=['auto', 'ball_tree', 'kd_tree', 'brute']
                  )

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

from sklearn.cross_validation import train_test_split, StratifiedShuffleSplit
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import classification_report

# Create training sets and test sets
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)

# Cross-validation for parameter tuning in grid search 
sss = StratifiedShuffleSplit(
    labels_train,
    n_iter = 20,
    test_size = 0.5,
    random_state = 0
    )

# Create, fit, and make predictions with grid search
gs = GridSearchCV(pipeline,
	              param_grid=parameters,
	              scoring="f1",
	              cv=sss,
	              error_score=0)
gs.fit(features_train, labels_train)
labels_predictions = gs.predict(features_test)

# Pick the classifier with the best tuned parameters
clf = gs.best_estimator_
print "\n", "Best parameters are: ", gs.best_params_, "\n"

# Print features selected
features_selected_bool = clf.named_steps['feature_selection'].get_support()
features_selected_list = [x for x, y in zip(features_list[1:], features_selected_bool) if y]
print "The ", len(features_selected_list), " features selected are: ", features_selected_list, "\n"

# Print classification report (focus on precision and recall)
report = classification_report( labels_test, labels_predictions )
print(report)

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)