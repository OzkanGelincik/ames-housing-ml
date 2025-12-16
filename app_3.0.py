import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify

# ==================================================
# 1. INITIALIZE APP
# ==================================================
app = Flask(__name__)

# ==================================================
# 2. CRITICAL: DEFINE CUSTOM FUNCTIONS
# ==================================================
# This function MUST exist here so the pickle knows what to look for.
# It must match the definition in your notebook exactly.
def cast_to_str(x):
    return x.astype(str)

# ==================================================
# 3. LOAD ASSETS
# ==================================================
print("Loading Production Pipeline and Column Definitions...")

try:
    # Now that 'cast_to_str' is defined above, this load will succeed
    model = joblib.load('ames_housing_super_model_production.pkl')

    expected_columns = joblib.load('ames_model_columns.pkl')

    print("✅ Model & Columns loaded successfully!")

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    print("   Did you run the Production Notebook to generate the .pkl files?")

# ==================================================
# 4. DEFINE GUARDRAILS
# ==================================================
def apply_guardrails(input_df):
    """
    Applies sanity checks.
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
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # A. Receive Raw User Data
        json_data = request.get_json()
        input_df = pd.DataFrame([json_data])

        # B. THE BRIDGE (Reindexing)
        # Ensure we have 79 columns (missing ones become NaN)
        # Note: 'expected_columns' is now safely loaded
        input_df = input_df.reindex(columns=expected_columns)

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
