# bug_model_training.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# 1️⃣ Load dataset
df = pd.read_csv("bug_reports.csv")

# 2️⃣ Keep only useful columns
df = df[['component_name', 'product_name', 'short_description', 'long_description',
         'resolution_category', 'status_category', 'quantity_of_votes', 'quantity_of_comments', 'severity_category']]

# 3️⃣ Drop missing rows
df.dropna(inplace=True)

# 4️⃣ Combine short + long description into one column
df["full_description"] = df["short_description"] + " " + df["long_description"]

# 5️⃣ Convert text columns to category codes
label_cols = ['component_name', 'product_name', 'resolution_category', 'status_category']
for col in label_cols:
    df[col] = df[col].astype('category').cat.codes

# 6️⃣ Define features (X) and target (y)
X = df[['component_name', 'product_name', 'resolution_category', 'status_category',
        'quantity_of_votes', 'quantity_of_comments']]
y = df['severity_category']

# 7️⃣ Encode target labels
le = LabelEncoder()
y = le.fit_transform(y)

# 8️⃣ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 9️⃣ Train model
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# 🔟 Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# 1️⃣1️⃣ Save model + label encoder
joblib.dump(model, "bug_severity_model.pkl")
joblib.dump(le, "severity_label_encoder.pkl")

print("✅ Model trained and saved successfully.")
