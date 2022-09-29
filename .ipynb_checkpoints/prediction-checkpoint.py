#import joblib

# Import file/data management
import json
import numpy as np
import pandas as pd

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

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
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score, make_scorer, confusion_matrix, plot_confusion_matrix

# Hide some warnings
import warnings
warnings.filterwarnings('ignore')


def model_performance_classification(model, name, X_test, target):
    '''
    Test classification scores for a given model
    '''

    # Run a prediction
    predictions = model.predict(X_test)

    # Calculate performance metrics
    accuracy  = accuracy_score(target, predictions)
    recall    = recall_score(target, predictions, average='macro')
    precision = precision_score(target, predictions, average='macro')
    f1        = f1_score(target, predictions, average='macro')

    print(accuracy, recall, precision, f1)
    return pd.DataFrame({
            'accuracy'  : [accuracy],
            'recall'    : [recall],
            'precision' : [precision],
            'f1'        : [f1]})


def build_confusion_matrix(model, name, X_test, target):
    '''
    Build a confusion matrix to understand classifications
    '''

    # Build matrix
    y_pred = model.predict(X_test)
    cm     = confusion_matrix(y_pred, target)

    # Calculate confusion matrix values for 2x2
    false_pos = cm.sum(axis=0) - np.diag(cm)
    false_neg = cm.sum(axis=1) - np.diag(cm)
    true_pos  = np.diag(cm)
    true_neg  = cm.sum() - (false_pos + false_neg + true_pos)

    TPR = true_pos / (true_pos+false_neg) # Sensitivity / true positive rate
    TNR = true_neg / (true_neg+false_neg) # Specificity / true negative rate
    FPR = false_neg / (false_pos+true_neg) # Fall out / False positive rate
    FNR = false_neg / (true_pos+false_neg) # False negative rate

    print(TPR.sum(), FNR.sum(), FPR.sum(), TNR.sum())

    total    = TPR.sum() + FNR.sum() + FPR.sum() + TNR.sum()
    percents = [round((TPR.sum()/total)*100, 2), 
                round((FNR.sum()/total)*100, 2),
                round((FPR.sum()/total)*100, 2),
                round((TNR.sum()/total)*100, 2)]
    sums     = [TPR.sum(), FNR.sum(), FPR.sum(), TNR.sum()]
    labels   = np.asarray([f'{sums[0]}\n{percents[0]}%',
                f'{sums[1]}\n{percents[1]}%',
                f'{sums[2]}\n{percents[2]}%',
                f'{sums[3]}\n{percents[3]}%']).reshape(2,2)


    plt.figure(figsize=(6,4))
    sns.heatmap(np.asarray(sums).reshape(2,2), annot=labels, fmt='')
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig(f'{name}_confusion_matrix.png')


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
cv_results = []
model_names = []
results= pd.DataFrame({'Name': [],
                          'Accuracy': [],
                          'Recall': [],
                          'Precision': [],
                          'F1': []})
print('Model\tCV_score\tV_score')
for name, model in models:
    # Cross-validate
    cv_result = cross_val_score(estimator=model, X=X_train, y=y_train, scoring=scorer, cv=5, error_score='raise')
    model_names.append(name)
    cv_results.append(cv_result)
    
    # Fit and validate
    model.fit(X_train, y_train)
    perf_vals = model_performance_classification(model, name, X_test, y_test)
    results = pd.concat([results, perf_vals])

    # Build Confusion Matrix
    #build_confusion_matrix(model, name, X_test, y_test)

# Output results table
results.to_csv('performance_results.tsv', sep='\t')

# Visualize cross-validation
fig = plt.figure(figsize=(10,7))
fig.suptitle('Algorithm Comparison')
ax = fig.add_subplot(111)
plt.boxplot(cv_results)
ax.set_xticklabels(model_names)
plt.savefig('cross-val.png')

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
