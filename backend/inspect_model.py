import joblib
import pprint
import os

p = os.path.dirname(__file__)
model_path = os.path.join(p, 'bug_severity_model.pkl')
print('Loading model from', model_path)
model = joblib.load(model_path)
print('\nModel type:', type(model))

try:
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    if isinstance(model, Pipeline):
        print('Pipeline steps:', list(model.named_steps.keys()))
        pre = model.named_steps.get('preprocessor', None)
        print('Preprocessor type:', type(pre))
        # Try to show ColumnTransformer transformers and their column names
        if isinstance(pre, ColumnTransformer):
            print('\nColumnTransformer transformers:')
            for name, trans, cols in pre.transformers:
                print(' -', name, '->', type(trans), 'columns:', cols)
        else:
            # Some pipelines use a custom preprocessor object
            try:
                print('\npreprocessor details:', dir(pre))
            except:
                pass
    else:
        print('Not a Pipeline. Showing attributes:')
        pprint.pprint([attr for attr in dir(model) if not attr.startswith('_')][:200])

except Exception as e:
    print('Error while inspecting pipeline:', e)

# If model saved feature names separately, print if available
features_path = os.path.join(p, 'model_features.pkl')
if os.path.exists(features_path):
    try:
        feats = joblib.load(features_path)
        print('\nLoaded model_features.pkl (len={}):'.format(len(feats)))
        if len(feats) < 50:
            pprint.pprint(feats)
        else:
            print('... (too many to display)')
    except Exception as e:
        print('Could not load model_features.pkl:', e)
else:
    print('\nmodel_features.pkl not found in backend folder')

# Done
print('\nDone')
