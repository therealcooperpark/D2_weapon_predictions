import joblib
import json
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn import tree

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
element_dummies = pd.get_dummies(df['element_class'])
df = pd.concat([df, ammo_dummies, element_dummies], axis=1)

# 4) Drop non-stat columns
df = df.drop(columns=['id', 'name', 'icon', 'watermark', 'screenshot',
                      'flavor_text', 'weapon_tier', 'powercap', 'perks',
                      'frame.name', 'frame.description', 'frame.icon',
                      'ammo_type', 'element_class'])

# 5) Replace NaN values with -1 to separate from real values
df.fillna(-1, inplace=True)

###################
# Build the model #
###################

# Create input and output
X = df.drop(columns=['weapon_type'])
y = df['weapon_type']

# Create train/test datasets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Build the model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Test the model
predictions = model.predict(X_test)

# Measure accuracy
accuracy = accuracy_score(y_test, predictions)
print('Accuracy: {0}'.format(accuracy))

# Visualize Decision Tree
class_names = y.unique()
class_names.sort()
feature_names = list(X.columns)
tree.export_graphviz(model, out_file='decision_tree.dot', feature_names=feature_names,
                    class_names=class_names, label='all', rounded=True, filled=True)
