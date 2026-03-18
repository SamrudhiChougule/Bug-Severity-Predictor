from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

model_path = os.path.join(os.path.dirname(__file__), "bug_severity_model.pkl")
model = joblib.load(model_path)

try:
    features_path = os.path.join(os.path.dirname(__file__), "model_features.pkl")
    model_features = joblib.load(features_path)
except:
    model_features = None

openapi_spec = None
openapi_path = os.path.join(os.path.dirname(__file__), 'openapi.json')
if os.path.exists(openapi_path):
    try:
        with open(openapi_path, 'r', encoding='utf-8') as f:
            openapi_spec = json.load(f)
    except Exception:
        openapi_spec = None

def load_options_from_dataset():
    """Load unique values from the dataset for dropdown options."""
    try:
        dataset_path = os.path.join(os.path.dirname(__file__), "bug_dataset.csv")
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path, nrows=0)  # Just read headers first
            if all(col in df.columns for col in ['product_name', 'component_name', 'resolution_category', 'status_category']):
                df = pd.read_csv(dataset_path)
                return {
                    "product_name": sorted(df['product_name'].unique().tolist()),
                    "component_name": sorted(df['component_name'].unique().tolist()),
                    "resolution_category": sorted(df['resolution_category'].unique().tolist()),
                    "status_category": sorted(df['status_category'].unique().tolist())
                }
    except Exception as e:
        print(f"Warning: Could not load options from dataset: {e}")
    
    return {
        "product_name": ["FIREFOX", "THUNDERBIRD", "CORE", "TOOLKIT", "DEVTOOLS"],
        "component_name": ["General", "Backend", "UI", "Networking", "Security"],
        "resolution_category": ["fixed"],
        "status_category": ["closed", "resolved"]
    }

OPTIONS = load_options_from_dataset()


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "✅ Bug Severity Predictor API is Running!"})


@app.route('/options', methods=['GET'])
def get_options():
    return jsonify(OPTIONS)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No input data provided."})
        is_valid, errors, cleaned = validate_input(data)
        if not is_valid:
            return jsonify({"status": "error", "message": "Invalid input.", "errors": errors}), 400

        df = pd.DataFrame([cleaned])

        try:
            prediction = model.predict(df)[0]
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Model prediction failed: {str(e)}"
            }), 500

        import datetime
        
        cleaned['predicted_severity'] = str(prediction)
        cleaned['prediction_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        all_dataset_columns = [
            'bug_id', 'creation_date', 'component_name', 'product_name',
            'short_description', 'long_description', 'assignee_name', 'reporter_name',
            'resolution_category', 'resolution_code', 'status_category', 'status_code',
            'update_date', 'quantity_of_votes', 'quantity_of_comments',
            'resolution_date', 'bug_fix_time', 'predicted_severity', 'prediction_timestamp'
        ]
        
        log_entry = {}
        for col in all_dataset_columns:
            log_entry[col] = cleaned.get(col, '')
        
        log_df = pd.DataFrame([log_entry])

        log_file = "predictions_log.csv"
        try:
            if not os.path.exists(log_file):
                log_df.to_csv(log_file, index=False)
            else:
                log_df.to_csv(log_file, mode='a', header=False, index=False)
        except PermissionError:
            pass
        except Exception as e:
            print(f"Warning: Could not write to predictions log: {e}")
            pass

        return jsonify({
            "status": "success",
            "predicted_severity": str(prediction)
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


def validate_input(data: dict):
    """Validate and normalize incoming JSON payload.

    Returns (is_valid: bool, errors: list[str], cleaned: dict)
    """
    errors = []
    cleaned = dict(data) if isinstance(data, dict) else {}

    desc_candidates = ['full_description', 'long_description', 'short_description', 'description', 'sd']
    found_desc = next((d for d in desc_candidates if d in cleaned and str(cleaned.get(d, '')).strip()), None)
    if not found_desc:
        errors.append('At least one description field is required: full_description, long_description, or short_description')
    else:
        if 'full_description' not in cleaned or not str(cleaned.get('full_description', '')).strip():
            short_desc = str(cleaned.get('short_description', '')).strip()
            long_desc = str(cleaned.get('long_description', '')).strip()
            if short_desc and long_desc:
                cleaned['full_description'] = f"{short_desc} {long_desc}".strip()
            elif short_desc:
                cleaned['full_description'] = short_desc
            elif long_desc:
                cleaned['full_description'] = long_desc
            else:
                cleaned['full_description'] = str(cleaned.get(found_desc, '')).strip()

    for fld in ['component_name', 'product_name', 'resolution_category', 'status_category']:
        if fld not in cleaned or not str(cleaned.get(fld, '')).strip():
            errors.append(f"'{fld}' is required and must be a non-empty string")

    for n in ['quantity_of_votes', 'quantity_of_comments']:
        val = cleaned.get(n, 0)
        try:
            cleaned[n] = int(val)
            if cleaned[n] < 0:
                cleaned[n] = 0
        except Exception:
            cleaned[n] = 0
            errors.append(f"'{n}' should be an integer; defaulting to 0")

    is_valid = len([e for e in errors if 'required' in e or 'description' in e]) == 0
    return is_valid, errors, cleaned


@app.route('/openapi.json', methods=['GET'])
def openapi_json():
    if openapi_spec is not None:
        return jsonify(openapi_spec)
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "Bug Severity Predictor API", "version": "1.0.0"},
        "paths": {
            "/predict": {
                "post": {
                    "summary": "Predict bug severity",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    },
                    "responses": {"200": {"description": "prediction result"}}
                }
            }
        }
    }
    return jsonify(spec)


@app.route('/analytics/summary', methods=['GET'])
def analytics_summary():
    try:
        log_file = "predictions_log.csv"
        if not os.path.exists(log_file):
            return jsonify({"status": "error", "message": "No predictions log available."}), 404

        df = pd.read_csv(log_file)

        # Apply filters if provided
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        product = request.args.get('product')
        component = request.args.get('component')
        severity = request.args.get('severity')

        if date_from:
            df = df[df['prediction_timestamp'] >= date_from]
        if date_to:
            df = df[df['prediction_timestamp'] <= date_to]
        if product:
            df = df[df['product_name'] == product]
        if component:
            df = df[df['component_name'] == component]
        if severity:
            df = df[df['predicted_severity'] == severity]

        total_predictions = len(df)
        if total_predictions == 0:
            return jsonify({
                "status": "success",
                "total_predictions": 0,
                "average_bug_fix_time": 0,
                "most_common_severity": "N/A",
                "severity_counts": {},
                "product_counts": {},
                "component_counts": {}
            })

        avg_bug_fix_time = df['bug_fix_time'].mean() if 'bug_fix_time' in df.columns else 0
        most_common_severity = df['predicted_severity'].mode().iloc[0] if not df['predicted_severity'].empty else "N/A"

        severity_counts = df['predicted_severity'].value_counts().to_dict()
        product_counts = df['product_name'].value_counts().to_dict() if 'product_name' in df.columns else {}
        component_counts = df['component_name'].value_counts().to_dict() if 'component_name' in df.columns else {}

        return jsonify({
            "status": "success",
            "total_predictions": total_predictions,
            "average_bug_fix_time": round(avg_bug_fix_time, 2),
            "most_common_severity": most_common_severity,
            "severity_counts": severity_counts,
            "product_counts": product_counts,
            "component_counts": component_counts
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/analytics/charts', methods=['GET'])
def analytics_charts():
    try:
        log_file = "predictions_log.csv"
        if not os.path.exists(log_file):
            return jsonify({"status": "error", "message": "No predictions log available."}), 404

        df = pd.read_csv(log_file)

        # Apply filters if provided
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        product = request.args.get('product')
        component = request.args.get('component')
        severity = request.args.get('severity')

        if date_from:
            df = df[df['prediction_timestamp'] >= date_from]
        if date_to:
            df = df[df['prediction_timestamp'] <= date_to]
        if product:
            df = df[df['product_name'] == product]
        if component:
            df = df[df['component_name'] == component]
        if severity:
            df = df[df['predicted_severity'] == severity]

        # Prepare data for charts
        severity_distribution = df['predicted_severity'].value_counts().to_dict() if not df.empty else {}

        # Predictions trend (daily)
        df['prediction_date'] = pd.to_datetime(df['prediction_timestamp']).dt.date
        trend_data = df.groupby('prediction_date').size().to_dict() if not df.empty else {}

        # Top products
        product_distribution = df['product_name'].value_counts().to_dict() if 'product_name' in df.columns and not df.empty else {}

        # Component distribution
        component_distribution = df['component_name'].value_counts().to_dict() if 'component_name' in df.columns and not df.empty else {}

        # Resolution category breakdown
        resolution_distribution = df['resolution_category'].value_counts().to_dict() if 'resolution_category' in df.columns and not df.empty else {}

        # Status category breakdown
        status_distribution = df['status_category'].value_counts().to_dict() if 'status_category' in df.columns and not df.empty else {}

        # Bug fix time histogram (bins)
        if 'bug_fix_time' in df.columns and not df.empty:
            bug_fix_times = df['bug_fix_time'].dropna().tolist()
            if bug_fix_times:
                # Create histogram bins
                import numpy as np
                hist, bin_edges = np.histogram(bug_fix_times, bins=10)
                bug_fix_histogram = {
                    "bins": bin_edges.tolist(),
                    "counts": hist.tolist()
                }
            else:
                bug_fix_histogram = {"bins": [], "counts": []}
        else:
            bug_fix_histogram = {"bins": [], "counts": []}

        return jsonify({
            "status": "success",
            "severity_distribution": severity_distribution,
            "trend_data": trend_data,
            "product_distribution": product_distribution,
            "component_distribution": component_distribution,
            "resolution_distribution": resolution_distribution,
            "status_distribution": status_distribution,
            "bug_fix_histogram": bug_fix_histogram
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/docs', methods=['GET'])
def docs_ui():
    html = '''
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Bug Severity Predictor API Docs</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
      </head>
      <body>
        <div id="swagger-ui"></div>
        <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
        <script>
          window.onload = function() {
            const ui = SwaggerUIBundle({
              url: '/openapi.json',
              dom_id: '#swagger-ui'
            });
          };
        </script>
      </body>
    </html>
    '''
    return html


if __name__ == "__main__":
    print("🚀 Running Bug Severity Predictor API on http://127.0.0.1:5000/")
    app.run(debug=True)
