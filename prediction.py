import joblib
import json
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree

def build_decisiontree_model(dataset, target_col):
    # Build a Decision Tree model given data and target column

    # Organize data
    X = dataset.drop(columns=[target_col])
    y = dataset[target_col]

    # Create train/test datasets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Build the model
    model = DecisionTreeClassifier()
    model.fit(X_train, y_train)

    # Test predictions
    predictions = model.predict(X_test)

    # Test accuracy
    accuracy = accuracy_score(y_test, predictions)

    return model, accuracy


def visualize_decisiontree(model, df, target_col, outfile):
    # Write out visualize tree model given data and target column
    class_names = df[target_col].unique()
    class_names.sort()
    feature_names = list(df.drop(columns=[target_col]).columns)
    tree.export_graphviz(model, out_file=outfile, feature_names=feature_names,
                         class_names=class_names, label='all', rounded=True, filled=True)
    

# Read database
with open('data/weapons/all.json', 'r') as json_file:
    js = json.load(json_file)
df = pd.json_normalize(js)

#####################
# Clean up the data #
#####################

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

########################
# Build original model #
########################

# Build the model
std_df = df.drop(columns=['perks', 'frame.name'])
std_model, std_accuracy = build_decisiontree_model(std_df, 'weapon_type')
print(f'Standard model accuracy: {std_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(std_model, std_df, 'weapon_type', 'std_decision_tree.dot')

#############################
# Build model w/o ammo type #
#############################

# Build the model
df_noammo = std_df.drop(columns=ammo_cols)
noammo_model, noammo_accuracy = build_decisiontree_model(df_noammo, 'weapon_type')
print(f'No ammo model accuracy: {noammo_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(noammo_model, df_noammo, 'weapon_type', 'noammo_decision_tree.dot')


################################
# Build model w/o element type #
################################

# Build the model
df_noelement = std_df.drop(columns=element_cols)
noelement_model, noelement_accuracy = build_decisiontree_model(df_noelement, 'weapon_type')
print(f'No element model accuracy: {noelement_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(noelement_model, df_noelement, 'weapon_type', 'noelement_decision_tree.dot')


###################################
# Build model w/o element or ammo #
###################################

# Build the model
df_noele_noammo = std_df.drop(columns=element_cols+ammo_cols)
noele_noammo_model, noele_noammo_accuracy = build_decisiontree_model(df_noele_noammo, 'weapon_type')
print(f'No element and no ammo model accuracy: {noele_noammo_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(noele_noammo_model, df_noele_noammo, 'weapon_type', 'noele_noammo_decision_tree.dot')

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

###################################
#  weapon+frame no element type   #
###################################

# Build the model
df_frame_noele = df_frame.drop(columns=element_cols)
frame_noele_model, frame_noele_accuracy = build_decisiontree_model(df_frame_noele, 'weapon_frame')
print(f'No element model predicting weapon and frame: {frame_noele_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(frame_noele_model, df_frame_noele, 'weapon_frame', 'noele_frame_decision_tree.dot')

##################################
#   weapon+frame no ele no ammo  #
##################################

# Build the model
df_frame_noele_noammo = df_frame.drop(columns=element_cols+ammo_cols)
frame_noele_noammo_model, frame_noele_noammo_accuracy = build_decisiontree_model(df_frame_noele_noammo, 'weapon_frame')
print(f'No element no ammo model predicting weapon and frame: {frame_noele_noammo_accuracy}')

# Visualize Decision Tree
visualize_decisiontree(frame_noele_noammo_model, df_frame_noele_noammo, 'weapon_frame', 'noele_noammo_frame_decision_tree.dot')
