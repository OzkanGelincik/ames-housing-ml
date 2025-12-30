import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# ==========================================
# 1. CRITICAL: DEFINE CUSTOM FUNCTIONS FIRST
# ==========================================
# This must match the definition used during training exactly.
def cast_to_str(x):
    return x.astype(str)

# ==========================================
# 2. SETUP
# ==========================================
# Load your production model artifacts
MODELS_DIR = Path("models")

print("Loading model...")
# Now that cast_to_str is defined above, this will work
model = joblib.load(MODELS_DIR / 'ames_housing_super_model_production.pkl')
model_columns = joblib.load(MODELS_DIR / 'ames_model_columns.pkl')
model_defaults = joblib.load(MODELS_DIR / 'ames_model_defaults.pkl')
print("✅ Model loaded successfully!")

# ==========================================
# 3. DEFINE RENOVATIONS
# ==========================================
# Structure: Name -> {Feature to change, New Value, Estimated Cost}
# PDATE RENOVATIONS DEFINITION
renovations = {
    "Luxury Kitchen Upgrade": {
        "changes": {
            "KitchenQual": "Ex"
        },
        "cost": 45000
    },
    "Add Garage (2-Car)": {
        "changes": {
            "GarageCars": 2,
            "GarageArea": 576,       # Standard 24x24 garage size
            "GarageType": "Attchd",  # Ensure it has a valid type
            "GarageFinish": "Unf",   # Assume unfinished to be safe
            "GarageYrBlt": 2005  # <--- CRITICAL ADDITION
        },
        "cost": 45000
    },
    "Finish Basement (500 sqft)": {
        "changes": {
            "BsmtFinSF1": 500,       # Add 500 finished
            "TotalBsmtSF": 500       # Ensure Total grows (if it was 0)
            # Note: We will handle the "add" logic in the loop carefully
        },
        "cost": 30000
    },
    "Install Central Air": {
        "changes": {
            "CentralAir": "Y"
        },
        "cost": 12000
    },
    "Add Fireplace": {
        "changes": {
            "Fireplaces": 1,
            "FireplaceQu": "Gd" # Give it a quality, otherwise it's "1 fireplace" with "None" quality
        },
        "cost": 5000
    }
}

# ==========================================
# 4. SELECT A BASE HOUSE
# ==========================================
# Create a synthetic "Fixer Upper" based on your model defaults
base_house = pd.DataFrame([model_defaults])
base_house['KitchenQual'] = 'TA'
base_house['GarageCars'] = 0
base_house['CentralAir'] = 'N'
base_house['Fireplaces'] = 0
base_house['BsmtFinSF1'] = 0

# Ensure columns align
base_house = base_house.reindex(columns=model_columns).fillna(model_defaults)

# ==========================================
# 5. RUN SIMULATION
# ==========================================
results = []

# Step A: Get Baseline Price
base_price = model.predict(base_house)[0]
print(f"🏠 Base House Price: ${base_price:,.2f}\n")

# UPDATED SIMULATION LOOP
for name, params in renovations.items():
    # Create a 'Digital Twin'
    renovated_house = base_house.copy()

    # Apply ALL linked changes for this renovation
    for feature, new_value in params['changes'].items():

        # Special Logic for Basement (Adding to existing)
        if feature in ['BsmtFinSF1', 'TotalBsmtSF'] and "Basement" in name:
             # If we are finishing a basement that was empty, we assume we are using existing space
             # UNLESS the base house had TotalBsmtSF=0.
             # Let's assume we are adding to the Finished count.
             if feature == 'TotalBsmtSF':
                 # Only increase total if it was 0 (digging a basement)
                 # otherwise assume we are finishing existing empty space.
                 if renovated_house[feature].iloc[0] == 0:
                     renovated_house[feature] = new_value
             else:
                 renovated_house[feature] += new_value

        else:
            # Standard Overwrite
            renovated_house[feature] = new_value

    # Step B: Predict New Price
    new_price = model.predict(renovated_house)[0]

    # Step C: Calculate Economics
    value_lift = new_price - base_price
    cost = params['cost']
    roi = ((value_lift - cost) / cost) * 100

    results.append({
        "Renovation": name,
        "Cost": cost,
        "Value Lift": value_lift,
        "ROI (%)": roi
    })

# ==========================================
# 6. DISPLAY RESULTS
# ==========================================
results_df = pd.DataFrame(results).sort_values("ROI (%)", ascending=False)

print(results_df.to_string(index=False, formatters={
    'Cost': '${:,.0f}'.format,
    'Value Lift': '${:,.2f}'.format,
    'ROI (%)': '{:,.1f}%'.format
}))
