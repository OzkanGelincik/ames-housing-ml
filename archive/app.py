import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from preprocessing import CorrelationThreshold, FeatureEngineer  # <--- Clean Import!

# 1. INITIALIZE THE APP
app = Flask(__name__)

# 2. LOAD MODEL & COLUMNS
print("Loading model and columns...")
try:
    model = joblib.load('ames_housing_super_model.pkl')
    model_columns = joblib.load('model_columns.pkl')
    print("✅ Model & Columns loaded successfully!")
except Exception as e:
    print(f"❌ Error loading files: {e}")

# 3. DEFINE GUARDRAILS
def apply_guardrails(input_df):
    safe_df = input_df.copy()
    if 'GrLivArea' in safe_df.columns and safe_df['GrLivArea'].iloc[0] > 10000:
        print("⚠️ Guardrail: Capping SqFt")
        safe_df['GrLivArea'] = 10000
    if 'OverallQual' in safe_df.columns and safe_df['OverallQual'].iloc[0] > 10:
        safe_df['OverallQual'] = 10
    return safe_df

# 4. PREDICT ENDPOINT
@app.route('/predict', methods=['POST'])
def predict():
    try:
        json_data = request.get_json()
        input_df = pd.DataFrame([json_data])

        # --- FIX 1: ALIGN COLUMNS ---
        input_df = input_df.reindex(columns=model_columns, fill_value=np.nan)

        # --- FIX 2: HANDLE NaNs (Simple) ---
        # Fills missing values with 0 to prevent crashes
        input_df = input_df.fillna(0)

        # Apply Guardrails
        safe_df = apply_guardrails(input_df)

        # Predict
        predicted_price = model.predict(safe_df)[0]

        return jsonify({
            'status': 'success',
            'predicted_price': float(predicted_price),
            'currency': 'USD'
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
