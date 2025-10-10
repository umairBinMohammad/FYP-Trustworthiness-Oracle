import numpy as np
import pandas as pd

# === CONFIGURATION ===
# Example structure:
# Replace with your actual data.
# Each column is a model’s similarity scores.
# 'manual' is your ground-truth label (A or DA).
data = pd.DataFrame({
    'manual': ['DA', 'A', 'A', 'DA', 'DA', 'A', 'A', 'A', 'A', 'A'],
    'model1': [0, 0.11, 0.48, 0.13, 0.02, 0.18, 0.11, 0.13, 0.34, 0.37],
    'model2': [0.13, 0.25, 0.5, 0.2, 0.2, 0.41, 0.29, 0.26, 0.45, 0.33],
    'model3': [0.05, 0.18, 0.43, 0.21, 0.02, 0.29, 0.13, 0.18, 0.36, 0.35],
    'model4': [0.77, 0.81, 0.86, 0.82, 0.78, 0.83, 0.8, 0.81, 0.84, 0.85],
    'model5': [0.76, 0.76, 0.88, 0.79, 0.76, 0.79, 0.79, 0.78, 0.82, 0.82],
    'model6': [0.59, 0.63, 0.8, 0.67, -0.55, 0.67, 0.66, 0.67, 0.73, 0.72]

})

# === METRIC FUNCTION ===
def compute_metrics(y_true, y_score, thresholds):
    results = []

    for t in thresholds:
        TP = TN = FP = FN = 0
        for label, score in zip(y_true, y_score):
            if score > t and label == 'A':
                TP += 1
            elif score <= t and label == 'DA':
                TN += 1
            elif score > t and label == 'DA':
                FP += 1
            elif score <= t and label == 'A':
                FN += 1

        acc = (TP + TN) / max((TP + TN + FP + FN), 1)
        prec = TP / max((TP + FP), 1e-9)
        rec = TP / max((TP + FN), 1e-9)
        f1 = 2 * prec * rec / max((prec + rec), 1e-9)
        results.append((t, TP, TN, FP, FN, acc, f1))
    return pd.DataFrame(results, columns=['threshold', 'TP', 'TN', 'FP', 'FN', 'accuracy', 'F1'])

# === MAIN LOOP FOR ALL 5 MODELS ===
thresholds = np.arange(-1, 1.05, 0.05)
manual = data['manual']

summary = {}

for model in ['model1', 'model2', 'model3', 'model4', 'model5', 'model6']:
    metrics_df = compute_metrics(manual, data[model], thresholds)
    best = metrics_df.loc[metrics_df['F1'].idxmax()]
    summary[model] = {
        'best_threshold': best['threshold'],
        'best_F1': best['F1'],
        'accuracy_at_best_F1': best['accuracy']
    }
    print(f"\n=== {model.upper()} ===")
    print(best)
    print(metrics_df.head())  # optional: preview of table

# Convert summary to DataFrame for clarity
summary_df = pd.DataFrame(summary).T
print("\n=== SUMMARY OF BEST THRESHOLDS ===")
print(summary_df)
