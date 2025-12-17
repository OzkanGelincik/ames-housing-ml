import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from pathlib import Path 

# ==================================================
# 1. INITIALIZE APP & PATHS
# ==================================================
app = Flask(__name__)

# Define where the models live relative to this script
# If app_3.0.py is in the project root, this points to root/models/
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"

# ==================================================
# 2. CRITICAL: DEFINE CUSTOM FUNCTIONS
# ==================================================
# This function MUST exist here so the pickle knows what to look for.
# It must match the definition in your notebook exactly for pickel to work
def cast_to_str(x):
    return x.astype(str)

# ==================================================
# 3. LOAD ASSETS
# ==================================================
print(f"Loading Production Pipeline, Columns and Defaults from: {MODELS_DIR} ...")

try:
    # UPDATED: Use the new path logic and the filename you just saved
    model_path = MODELS_DIR / 'ames_housing_super_model_production.pkl'
    columns_path = MODELS_DIR / 'ames_model_columns.pkl'
    defaults_path = MODELS_DIR / 'ames_model_defaults.pkl' 

    # Now that 'cast_to_str' is defined above, this load will succeed
    model = joblib.load(model_path)
    expected_columns = joblib.load(columns_path)
    model_defaults = joblib.load(defaults_path)

    print("✅ Model & Columns loaded successfully!")

except FileNotFoundError as e:
    print(f"❌ FATAL ERROR: Could not find file. {e}")
    print(f"   Looking in: {MODELS_DIR}")
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")

# ==================================================
# 4. DEFINE GUARDRAILS
# ==================================================
def apply_guardrails(input_df):
    """
    Applies sanity checks to prevent unrealistic values.
    """
    safe_df = input_df.copy()

    # Cap Square Footage
    if 'GrLivArea' in safe_df.columns:
        safe_df['GrLivArea'] = safe_df['GrLivArea'].clip(upper=10000)

    # Cap Quality
    if 'OverallQual' in safe_df.columns:
        safe_df['OverallQual'] = safe_df['OverallQual'].clip(upper=10)

    return safe_df

# ==================================================
# 5. PREDICT ENDPOINT
# ==================================================
# ==================================================
# 5. PREDICT ENDPOINT
# ==================================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # A. Receive Raw User Data
        json_data = request.get_json()
        input_df = pd.DataFrame([json_data])

        # B. THE BRIDGE (Reindexing & Filling)
        # 1. Ensure we have the exact columns (creates NaNs for missing ones)
        input_df = input_df.reindex(columns=expected_columns)
        
        # 2. FILL MISSING VALUES (The Safety Net)
        # This uses the median/mode dict we saved to replace NaNs
        input_df = input_df.fillna(model_defaults) # <--- CRITICAL FIX

        # C. Apply Guardrails
        input_df = apply_guardrails(input_df)

        # D. Predict
        predicted_price = model.predict(input_df)[0]
        
        return jsonify({
            'status': 'success', 
            'predicted_price': float(predicted_price),
            'currency': 'USD',
            'version': '3.0 (Full Pipeline)'
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)