import joblib
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from pathlib import Path 
from typing import Optional # <--- Fixed: This is now included
from pydantic import BaseModel, Field, ValidationError, ConfigDict # <--- Fixed: Added ConfigDict

# ==================================================
# 1. INITIALIZE APP & PATHS
# ==================================================
app = Flask(__name__)

# Define where the models live relative to this script
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"

# ==================================================
# 2. CRITICAL: DEFINE CUSTOM FUNCTIONS
# ==================================================
def cast_to_str(x):
    return x.astype(str)

# ==================================================
# 3. LOAD ASSETS
# ==================================================
print(f"Loading Production Pipeline, Columns and Defaults from: {MODELS_DIR} ...")

try:
    model_path = MODELS_DIR / 'ames_housing_super_model_production.pkl'
    columns_path = MODELS_DIR / 'ames_model_columns.pkl'
    defaults_path = MODELS_DIR / 'ames_model_defaults.pkl' 

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
class HouseData(BaseModel):
    # --- 1. REQUIRED FIELDS ---
    GrLivArea: float = Field(..., gt=100, lt=10000, description="Above ground living area in sq ft")
    YearBuilt: int = Field(..., gt=1800, lt=2030)
    OverallQual: int = Field(..., ge=1, le=10, description="Rates the overall material and finish (1-10)")
    Neighborhood: str 

    # --- 2. RENOVATION FIELDS (Optional) ---
    KitchenQual: Optional[str] = Field(None, description="Ex, Gd, TA, Fa, Po")
    FullBath: Optional[int] = Field(None, ge=0, le=5)
    HalfBath: Optional[int] = Field(None, ge=0, le=4)
    
    GarageCars: Optional[int] = Field(None, ge=0, le=5)
    GarageArea: Optional[float] = Field(None, ge=0)
    GarageType: Optional[str] = None

    TotalBsmtSF: Optional[float] = Field(None, ge=0)
    BsmtFinSF1: Optional[float] = Field(None, ge=0)
    BsmtQual: Optional[str] = None
    
    WoodDeckSF: Optional[float] = Field(None, ge=0)
    OpenPorchSF: Optional[float] = Field(None, ge=0)
    PoolArea: Optional[float] = Field(None, ge=0)
    Fireplaces: Optional[int] = Field(None, ge=0)
    CentralAir: Optional[str] = None

    # --- 3. STRUCTURAL FIELDS (Optional) ---
    LotArea: Optional[float] = Field(None, gt=0)
    LotFrontage: Optional[float] = Field(None, gt=0)
    BldgType: Optional[str] = None
    HouseStyle: Optional[str] = None
    OverallCond: Optional[int] = Field(None, ge=1, le=10)
    YearRemodAdd: Optional[int] = Field(None, ge=1900)

    # --- MAGIC SWITCH (UPDATED FOR PYDANTIC V2) ---
    # This replaces the old "class Config" to fix the warning
    model_config = ConfigDict(extra='allow')

# ==================================================
# 5. PREDICT ENDPOINT
# ==================================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Validate Input using Pydantic
        data = request.get_json()
        validated_data = HouseData(**data)
        
        # 2. Convert to DataFrame
        input_df = pd.DataFrame([validated_data.model_dump()])
        
        # 3. Align with Model Structure (Reindex)
        input_df = input_df.reindex(columns=expected_columns)
        
        # 4. Fill Missing Data with Defaults
        input_df = input_df.fillna(model_defaults)
        
        # 5. Predict
        prediction = model.predict(input_df)[0]
        
        return jsonify({
            "predicted_price": float(prediction),
            "status": "success",
            "version": "4.0 (Guardrails + Pydantic)"
        })

    except ValidationError as e:
        return jsonify({
            "error": "Validation Failed",
            "details": e.errors()
        }), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True, port=5000)
