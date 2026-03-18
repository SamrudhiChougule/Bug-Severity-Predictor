import joblib
import pandas as pd

model = joblib.load('bug_severity_model.pkl')

# Sample data matching the new dataset structure
sample = {
    'component_name': 'General',
    'product_name': 'FIREFOX',
    'short_description': 'App crashes when clicking Save',
    'long_description': 'When I click the Save button the app crashes with NullPointerException. Steps to reproduce: ...',
    'resolution_category': 'fixed',
    'status_category': 'resolved',
    'quantity_of_votes': 3,
    'quantity_of_comments': 1
}

df = pd.DataFrame([sample])

# Combine short and long descriptions into full_description (matching training logic)
df['short_description'] = df['short_description'].fillna('')
df['long_description'] = df['long_description'].fillna('')
df['full_description'] = (df['short_description'] + ' ' + df['long_description']).str.strip()

# Ensure expected columns exist (matching training features)
expected_columns = ['component_name', 'product_name', 'resolution_category',
                    'status_category', 'full_description',
                    'quantity_of_votes', 'quantity_of_comments']
for col in expected_columns:
    if col not in df.columns:
        if col in ['quantity_of_votes', 'quantity_of_comments']:
            df[col] = 0
        else:
            df[col] = ''

print('Prepared DataFrame:')
print(df[expected_columns].to_dict(orient='records'))

pred = model.predict(df[expected_columns])
print('\nPrediction result:', pred[0])
print('Predicted severity:', pred[0])
