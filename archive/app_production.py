import joblib
import pandas as pd
import numpy as np
import sklearn # <--- NEW IMPORT
from flask import Flask, request, jsonify
from sklearn import set_config

# Import custom class so joblib knows how to rebuild the model
from preprocessing import CorrelationThreshold

# -----------------------------------------------------------
# 1. INITIALIZE THE APP (This must come BEFORE the routes!)
# -----------------------------------------------------------
app = Flask(__name__)

# -----------------------------------------------------------
# 2. LOAD ARTIFACTS
# -----------------------------------------------------------
print("Loading Production Model & Columns...")
try:
    # Load the "Gold Standard" pipeline
    model = joblib.load('ames_housing_super_model_production.pkl')

    # Load the column list (for structural alignment)
    model_columns = joblib.load('model_columns.pkl')
    print("✅ Production Model loaded successfully!")
except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    print("Make sure you ran the 'production' notebook to generate the .pkl files.")

# -----------------------------------------------------------
# 3. DEFINE GUARDRAILS (Safety First)
# -----------------------------------------------------------
def apply_guardrails(input_df):
    """
    Clamps extreme outliers to prevent linear model extrapolation errors.
    """
    safe_df = input_df.copy()

    # Cap Square Footage at 10,000
    if 'GrLivArea' in safe_df.columns and safe_df['GrLivArea'].iloc[0] > 10000:
        print("⚠️ Guardrail Active: Capping SqFt to 10,000")
        safe_df['GrLivArea'] = 10000

    # Cap Overall Quality at 10
    if 'OverallQual' in safe_df.columns and safe_df['OverallQual'].iloc[0] > 10:
        safe_df['OverallQual'] = 10

    return safe_df

# -----------------------------------------------------------
# 5. DEFINE THE API ROUTE
# -----------------------------------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # A. Get Data
        json_data = request.get_json()
        input_df = pd.DataFrame([json_data])

        # B. Align Columns (Structure Check)
        # This ensures the dataframe has exactly 80 columns.
        # Missing columns are created and filled with NaN.
        # The Pipeline's SimpleImputer will handle these NaNs automatically.
        input_df = input_df.reindex(columns=model_columns)

        # C. Apply Guardrails (Safety Check)
        safe_df = apply_guardrails(input_df)

        # --- THE FIX IS HERE ---
        # We force Sklearn to use Pandas DataFrames just for this block of code.
        # This prevents the configuration from getting lost.
        with sklearn.config_context(transform_output="pandas"):
            predicted_price = model.predict(safe_df)[0]
        # -----------------------

        # E. Return Result
        return jsonify({
            'status': 'success',
            'predicted_price': float(predicted_price),
            'currency': 'USD',
            'model_version': 'Production Gold Standard'
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

# -----------------------------------------------------------
# 6. RUN THE SERVER
# -----------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)
