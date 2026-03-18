import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import classification_report
import joblib

# Step 1️⃣ Load dataset
df = pd.read_csv("bug_dataset.csv", sep=",", engine="python", on_bad_lines="skip")

# Step 2️⃣ Basic cleaning - drop rows with missing severity
df.dropna(subset=['severity_category'], inplace=True)

# Step 3️⃣ Combine short_description and long_description into full_description
# Handle missing values by filling with empty string
df['short_description'] = df['short_description'].fillna('')
df['long_description'] = df['long_description'].fillna('')
df['full_description'] = (df['short_description'] + ' ' + df['long_description']).str.strip()

# Drop rows where full_description is empty (no text to analyze)
df = df[df['full_description'].str.len() > 0]

# Step 4️⃣ Define features and label
X = df[['component_name', 'product_name', 'resolution_category', 'status_category', 
        'full_description', 'quantity_of_votes', 'quantity_of_comments']]
y = df['severity_category']

# Step 5️⃣ Define feature types
text_features = ['full_description']
categorical_features = ['component_name', 'product_name', 'resolution_category', 'status_category']
numeric_features = ['quantity_of_votes', 'quantity_of_comments']

# Step 6️⃣ Preprocessor setup
preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(stop_words='english', max_features=5000), 'full_description'),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
        ('num', StandardScaler(), numeric_features)
    ],
    remainder='drop'
)

# Step 7️⃣ Build model pipeline
model = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1))
])

# Step 8️⃣ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Step 9️⃣ Train the model
print("🔄 Training model...")
model.fit(X_train, y_train)

# Step 🔟 Evaluate
y_pred = model.predict(X_test)
print("\n📊 Model Evaluation:\n")
print(classification_report(y_test, y_pred))

# Step 1️⃣1️⃣ Save model and feature names
joblib.dump(model, "bug_severity_model.pkl")

try:
    model_features = preprocessor.get_feature_names_out()
except:
    model_features = []  # fallback if feature names unavailable

joblib.dump(model_features, "model_features.pkl")

print("\n✅ Model and feature list saved successfully!")
print(f"📊 Dataset info: {len(df)} rows, {len(y.unique())} severity classes")
print(f"📊 Severity classes: {sorted(y.unique())}")
