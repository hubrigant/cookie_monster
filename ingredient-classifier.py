from sklearn.neighbors import KNeighborsClassifier
from sklearn.cross_validation import KFold
import csv


# Feature lut
# 0: butter
# 1: graham crackers
# 2: vanilla wafers
# 3:


labels = []
features =[]
with open(ing_training.csv, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        labels.append(row[0])

classifier = KNeighborsClassifier(n_neighbors=5)
kf = KFold(len(features), n_folds=5, shuffle=True)
