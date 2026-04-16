"""
Train and save the tabular design-pattern classifier (RandomForest vs SVM).
Run from backend/:  python train_design_pattern_model.py
Requires: FINAL_DESIGNPATTERN_DATASET.csv (columns must match dp_tabular_features.FEATURE_COLUMN_ORDER + pattern, category)
Outputs: design_pattern_models/best_model.pkl, label_encoder.pkl, feature_columns.pkl
"""

import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

from dp_tabular_features import FEATURE_COLUMN_ORDER

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BACKEND_DIR, "FINAL_DESIGNPATTERNDB.csv")
OUT_DIR = os.path.join(BACKEND_DIR, "design_pattern_models")

def main():
    if not os.path.isfile(DATA_PATH):
        raise FileNotFoundError(f"Missing {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    missing = [c for c in FEATURE_COLUMN_ORDER if c not in df.columns]
    if missing:
        raise ValueError(f"CSV missing feature columns: {missing}")
    X = df[FEATURE_COLUMN_ORDER]
    y = df["pattern"]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=150,
            max_depth=8,
            class_weight="balanced",
            random_state=42,
        ),
        "SVM": SVC(
            probability=True,
            class_weight="balanced",
            kernel="rbf",
        ),
    }

    best_pipe = None
    best_name = None
    best_f1 = -1.0

    for name, clf in models.items():
        pipe = Pipeline(
            [
                ("scaler", StandardScaler()),
                ("model", clf),
            ]
        )
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        acc = accuracy_score(y_test, pred)
        f1 = f1_score(y_test, pred, average="macro")
        print(f"\n{name}")
        print("  Accuracy:", round(acc * 100, 2), "%")
        print("  Macro F1:", round(f1 * 100, 2), "%")
        if f1 > best_f1:
            best_f1 = f1
            best_pipe = pipe
            best_name = name

    print("\nBest model:", best_name)

    os.makedirs(OUT_DIR, exist_ok=True)
    joblib.dump(best_pipe, os.path.join(OUT_DIR, "best_model.pkl"))
    joblib.dump(le, os.path.join(OUT_DIR, "label_encoder.pkl"))
    joblib.dump(FEATURE_COLUMN_ORDER, os.path.join(OUT_DIR, "feature_columns.pkl"))

    print("Saved to", OUT_DIR)


if __name__ == "__main__":
    main()
