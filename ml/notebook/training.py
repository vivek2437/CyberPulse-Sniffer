
import kagglehub
bertvankeulen_cicids_2017_path = kagglehub.dataset_download('bertvankeulen/cicids-2017')

print('Data source import complete.')


import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, classification_report, roc_auc_score,
    confusion_matrix
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder, label_binarize

DATA_DIR = Path("/kaggle/input/cicids-2017")

csv_files = sorted(DATA_DIR.glob("*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

df_list = []
for f in csv_files:
    print("Loading:", f.name)
    df_part = pd.read_csv(f)
    df_list.append(df_part)

# Merge all parts
df = pd.concat(df_list, ignore_index=True)
print("Loaded shape:", df.shape)

merged_path = "cicids2017_merged.csv"
df.to_csv(merged_path, index=False)
print(f"Merged dataset saved to {merged_path}")

# ================================
# 2. Preprocessing
# ================================
df = df.dropna()
print("After dropna:", df.shape)

y = df["Label"]
X = df.drop(columns=["Label"])

# 🔎 Keep only numeric features
X = X.select_dtypes(include=[np.number])

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)
class_names = label_encoder.classes_
print("Classes:", class_names)

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print("Feature matrix shape:", X.shape)
print("Train/Test split:", X_train.shape, X_test.shape)

# ================================
# 3. Helper Functions
# ================================
def evaluate_model(name, model, X_test, y_test, label_encoder):
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"--- {name} ---")
    print("Accuracy:", acc)
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    # ROC AUC for multiclass
    try:
        y_score = model.predict_proba(X_test)
        y_bin = label_binarize(y_test, classes=np.arange(len(label_encoder.classes_)))
        auc = roc_auc_score(y_bin, y_score, average="macro", multi_class="ovr")
    except Exception:
        auc = None
    print("ROC AUC:", auc)

    cm = confusion_matrix(y_test, y_pred)
    print("Confusion matrix:\n", cm)

    #  TP, TN, FP, FN (for binary classes only)
    if len(label_encoder.classes_) == 2:
        tn, fp, fn, tp = cm.ravel()
        print(f" True Positive (TP): {tp}")
        print(f" False Positive (FP): {fp}")
        print(f" False Negative (FN): {fn}")
        print(f" True Negative (TN): {tn}")

    #  Percentage Analyzer
    per_class_stats = {}
    for i, cls in enumerate(label_encoder.classes_):
        correct = cm[i, i]
        total = cm[i, :].sum()
        acc_cls = correct / total if total > 0 else 0
        mis = 1 - acc_cls
        print(f"📊 {cls}: {correct}/{total} correct = {acc_cls*100:.2f}% | Misclassified = {mis*100:.2f}%")
        per_class_stats[cls] = acc_cls * 100

    return {
        "Model": name,
        "Accuracy": acc,
        "ROC_AUC": auc,
        **{f"{cls} Correct %": v for cls, v in per_class_stats.items()}
    }

def extract_features(model, X_train, name, top_k=15):
    """Extract feature importance for tree-based models"""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        feat_df = pd.DataFrame({
            "Feature": X_train.columns,
            f"{name}_Importance": importances
        }).sort_values(by=f"{name}_Importance", ascending=False).head(top_k)
        return feat_df
    else:
        return pd.DataFrame(columns=["Feature", f"{name}_Importance"])

# ================================
# 4. Feature Selection
# ================================
print("\n Running feature selection...")
fs_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
fs_model.fit(X_train, y_train)

feat_importances = pd.DataFrame({
    "Feature": X_train.columns,
    "Importance": fs_model.feature_importances_
}).sort_values(by="Importance", ascending=False)

TOP_K = 30
top_features = feat_importances.head(TOP_K)["Feature"].tolist()
print(f"Selected top {TOP_K} features:", top_features)

# Reduce datasets
X_train = X_train[top_features]
X_test = X_test[top_features]

feat_importances.to_csv("all_feature_importances.csv", index=False)
pd.DataFrame(top_features, columns=["TopFeatures"]).to_csv("selected_features.csv", index=False)

# ================================
# 5. Train Models on Selected Features
# ================================
results = []
feature_dfs = []

# Decision Tree
dt = DecisionTreeClassifier(max_depth=20, random_state=42)
dt.fit(X_train, y_train)
results.append(evaluate_model("Decision Tree", dt, X_test, y_test, label_encoder))
feature_dfs.append(extract_features(dt, X_train, "DecisionTree"))
joblib.dump(dt, "decision_tree.pkl")

# Random Forest
rf = RandomForestClassifier(n_estimators=150, max_depth=25, random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)
results.append(evaluate_model("Random Forest", rf, X_test, y_test, label_encoder))
feature_dfs.append(extract_features(rf, X_train, "RandomForest"))
joblib.dump(rf, "random_forest.pkl")

# XGBoost
xgb_clf = XGBClassifier(
    n_estimators=200,
    max_depth=10,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="mlogloss",
    use_label_encoder=False,
    random_state=42,
    n_jobs=-1
)
xgb_clf.fit(X_train, y_train)
results.append(evaluate_model("XGBoost", xgb_clf, X_test, y_test, label_encoder))
feature_dfs.append(extract_features(xgb_clf, X_train, "XGBoost"))
joblib.dump(xgb_clf, "xgboost.pkl")

# ================================
# 6. Save Results
# ================================
results_df = pd.DataFrame(results)
results_df.to_csv("model_results.csv", index=False)
print("\n📂 Results saved to model_results.csv")
print(results_df)

# ================================
# 7. Plot Feature Importances
# ================================
feat_all = feature_dfs[0]
for df_tmp in feature_dfs[1:]:
    feat_all = feat_all.merge(df_tmp, on="Feature", how="outer")

feat_all.fillna(0, inplace=True)
feat_all.to_csv("feature_importances_selected.csv", index=False)

plt.figure(figsize=(14, 8))
for col in feat_all.columns[1:]:
    sns.barplot(x="Feature", y=col, data=feat_all.head(10), label=col)
plt.xticks(rotation=90)
plt.title("Top Features (Selected Set)")
plt.ylabel("Importance Score")
plt.legend()
plt.tight_layout()
plt.show()
