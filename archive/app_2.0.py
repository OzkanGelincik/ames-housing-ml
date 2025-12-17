import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from preprocessing import CorrelationThreshold, FeatureEngineer  # <--- Clean Import!

# 1. INITIALIZE THE APP
app = Flask(__name__)

# 2. LOAD ASSETS
print("Loading model and defaults...")
try:
    # Load the trained model
    model = joblib.load('ames_housing_super_model.pkl')

    # Load the "Reference Book" of Medians and Modes
    model_defaults = joblib.load('model_defaults.pkl')

    # Extract the list of expected columns from the defaults dictionary keys
    expected_columns = list(model_defaults.keys())

    print("✅ Model & Defaults loaded successfully!")
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")

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

        # --- STEP A: ALIGN COLUMNS ---
        input_df = input_df.reindex(columns=expected_columns)

        # --- STEP B: SMART IMPUTATION ---
        # Fill NaNs using the Medians/Modes from model_defaults.pkl
        input_df = input_df.fillna(model_defaults)

        # --- STEP C: SAFETY FALLBACK ---
        input_df = input_df.fillna(0)
        
        # Apply Guardrails
        safe_df = apply_guardrails(input_df)
        
        # Predict
        predicted_price = model.predict(safe_df)[0]
        
        return jsonify({
            'status': 'success', 
            'predicted_price': float(predicted_price),
            'currency': 'USD',
            'version': '2.0 (Smart Imputation)'
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
