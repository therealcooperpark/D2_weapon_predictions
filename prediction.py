#import joblib

# Import file/data management
import json
import numpy as np
import pandas as pd

# Import models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
    BaggingClassifier)
from sklearn.tree import DecisionTreeClassifier

# Import stats
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, make_scorer

# Hide some warnings
import warnings
warnings.filterwarnings('ignore')


def model_performance_classification(model, y_test, target):
    '''
    Test classification scores for a given model
    '''

    # Run a prediction
    predictions = model.predict(y_test)

    # Calculate performance metrics
    accuracy  = accuracy_score(target, predictions)
    recall    = recall_score(target, predictions)
    precision = precision_score(target, predictions)
    f1        = f1_score(target, predictions)

    return pd.DataFrame({
            'accuracy'  : accuracy,
            'recall'    : recall,
            'precision' : precision,
            'f1'        : f1})


def build_confusion_matrix(model, X_test, target):
    '''
    Build a confusion matrix to understand classifications
    '''

    y_pred = model.predict(X_test)
    cm     = confusion_matrix(y_pred, target)
    scores = np.asarray(
             ['{0:0.0f}'.format(item) + '\n{0:.2%}'.format(item/cm.flatten().sum())
             for item in cm.flatten()]).reshape(2,2)
    print(scores)
    return None


def split_dataset(dataset, target_col, test_size=0.2):
    '''
    Make dataset, build test using test_ratio
    '''
    # Organize data
    X = dataset.drop(columns=[target_col])
    y = dataset[target_col]

    # Create train/test datasets
    return train_test_split(X, y, test_size=test_size, stratify=y)
   

def visualize_decisiontree(model, df, target_col, outfile):
    # Write out visualize tree model given data and target column
    class_names = df[target_col].unique()
    class_names.sort()
    feature_names = list(df.drop(columns=[target_col]).columns)
    tree.export_graphviz(model, out_file=outfile, feature_names=feature_names,
                         class_names=class_names, label='all', rounded=True, filled=True)



#####################
# Clean up the data #
#####################

# Read database
with open('data/weapons/all.json', 'r') as json_file:
    js = json.load(json_file)
df = pd.json_normalize(js)

# 1) Remove sunset gear
# (Assumes weapon type rules were adhered to better after sunsetting)
df = df[df['powercap'].isna()]

# 2) Keep only legendary gear
# (Exotics are unique and under legendary likely has worse stats in general)
# (Possibly worth experimenting as an alternate prediction though!)
df = df[df['weapon_tier'] == 'legendary']

# 3) Convert categorical columns into numerics
ammo_dummies = pd.get_dummies(df['ammo_type'])
ammo_cols = list(ammo_dummies.columns)
element_dummies = pd.get_dummies(df['element_class'])
element_cols = list(element_dummies.columns)
df = pd.concat([df, ammo_dummies, element_dummies], axis=1)

# 4) Remove unecessary columns (keeps perks and frame.name for future models)
df = df.drop(columns=['id', 'name', 'icon', 'watermark', 'screenshot',
                      'flavor_text', 'weapon_tier', 'powercap', 'frame.description', 
                      'frame.icon', 'ammo_type', 'element_class'])

# 5) Replace NaN values with -1 to separate from real values
df.fillna(-1, inplace=True)


##############################
#  Build models and datasets #
##############################

# Dataset with no perks or frame
std_df = df.drop(columns=['frame.name', 'perks'])
X_train, X_test, y_train, y_test = split_dataset(std_df, 'weapon_type')


# Models
models = [('decision_tree', DecisionTreeClassifier(random_state=1)),
          ('log_regression', LogisticRegression(random_state=1)),
          ('bagging', BaggingClassifier(random_state=1)),
          ('random_forest', RandomForestClassifier(random_state=1)),
          ('gbm', GradientBoostingClassifier(random_state=1)),
          ('adaboost', AdaBoostClassifier(random_state=1))]

###################
# Validate models #
###################

# Define scorer to optimize models for precision
# I want as many correct hits as possible, then investigate anything else individually
scorer = make_scorer(precision_score, average='macro')

# Cross-validate and validate with data
print('Model\tCV_score\tV_score')
for name, model in models:
    # Cross-validate
    cv_result = cross_val_score(estimator=model, X=X_train, y=y_train, scoring=scorer, cv=5, error_score='raise')
    
    # Fit and validate
    model.fit(X_train, y_train)
    recall = precision_score(y_test, model.predict(X_test), average='macro')
    print(f'{name}\t{cv_result.mean()}\t{recall}')

# TO DO: Visualize comparisons

# TO DO: Repeat with alternative datasets
'''
#############################
# Build model w/o ammo type #
#############################

# Build the model
df_noammo = std_df.drop(columns=ammo_cols)
noammo_model, noammo_accuracy = build_decisiontree_model(df_noammo, 'weapon_type')
print(f'No ammo model accuracy: {noammo_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(noammo_model, df_noammo, 'weapon_type', 'noammo_decision_tree.dot')


print('------------------------------\nWeapon+Frame models\n-----------------------------')
###################################
# Standard model for weapon+frame #
###################################

# Build the model
df_frame = df.drop(columns=['perks'])
df_frame['weapon_frame'] = df_frame['weapon_type'] + '-' + df_frame['frame.name']
df_frame = df_frame.drop(columns=['weapon_type', 'frame.name'])

frame_model, frame_accuracy = build_decisiontree_model(df_frame, 'weapon_frame')
print(f'Standard model predicting weapon and frame: {frame_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(frame_model, df_frame, 'weapon_frame', 'std_frame_decision_tree.dot')

###################################
#    weapon+frame no ammo type    #
###################################

# Build the model
df_frame_noammo = df_frame.drop(columns=ammo_cols)
frame_noammo_model, frame_noammo_accuracy = build_decisiontree_model(df_frame_noammo, 'weapon_frame')
print(f'No ammo model predicting weapon and frame: {frame_noammo_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(frame_noammo_model, df_frame_noammo, 'weapon_frame', 'noammo_frame_decision_tree.dot')
'''
