# 🏡 Ames Housing Price Prediction: Ensemble Architecture

### 🚀 **Test R² Score: 0.933**

This repository contains a robust machine learning pipeline designed to predict housing prices in Ames, Iowa. It utilizes a **Weighted Voting Ensemble** combining Linear Models (Lasso) and Gradient Boosted Trees (XGBoost, CatBoost) to achieve high accuracy while maintaining interpretability and safety against outliers.

---

## 📂 Repository Structure

This project is divided into two distinct phases:

### 1. 🔬 The Lab Notebook (`ames_housing_prices_modeling_master.ipynb`)
**"The Research Phase"**
- Extensive Exploratory Data Analysis (EDA).
- Model training: OLS, Ridge, Lasso, ElasticNet, SVR, Random Forest, XGBoost, CatBoost, and Voting (Ensemble) Regressors
- Feature Engineering experiments (Ordinal vs. One-Hot Encoding; incl. Total Square Footage, House Age, Total Bathrooms, and Longitude/Lattitude Mapping for Neighborhoods).
- Hyperparameter tuning via GridSearch.
- Stress Testing (e.g., The 'Ghost House' (0 SqFt), 'Impossible House' (Negative Area) and 'Mega-Mansion' (200k SqFt) simulations).
- Feature Importance Analysis (Model Coefficients, Feature Importances, Perfmuation Importance, and SHAP values).

### 2. 🏭 The Production Notebook (`ames_housing_prices_modeling_production.ipynb`)
**"The Deployment Phase"**
- A streamlined, clean execution pipeline (incl. the winning model 🏆).
- Consolidates preprocessing and modeling into a single `sklearn` Pipeline.
- Handles raw user input (JSON-style) with automatic imputation.
- Generates the final deployment artifacts (`.pkl` files).

---

## 🧪 API Verification & Testing

Once the server is running (`python app_3.0.py`), you can use the provided test scripts to verify model performance and safety guardrails.

| Script | Purpose |
| :--- | :--- |
| **`test_basic.py`** | **Connectivity Check.** Sends a standard request to ensure the API returns a valid price and HTTP 200 status. |
| **`test_guardrails.py`** | **Safety Check.** Stress tests the system with extreme inputs (e.g., 200k sq ft mansions) and missing data to ensure the pipeline doesn't crash. |
| **`test_comparison.py`** | **Logic Check.** Compares a standard house vs. a renovated house to ensure the model responds logically to improvements (Price increases). |

**To run a test:**
```bash
python test_basic.py
```

---

## 🧠 Model Architecture

The final "Super Model" is a **Voting Regressor** consisting of three distinct branches:

| Branch | Algorithm | Role | Preprocessing Strategy |
| :--- | :--- | :--- | :--- |
| **A** | **Lasso Regression** | Captures linear trends & baseline prices. | **One-Hot Encoding** + Standardization |
| **B** | **XGBoost** | Captures non-linear complexities. | **Ordinal Encoding** (Integer-based) |
| **C** | **CatBoost** | Handles categorical nuances high efficiency. | **Ordinal Encoding** (Integer-based) |

**Ensemble Weights:** Lasso (1) : XGBoost (2) : CatBoost (2)

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Core:** `scikit-learn`, `pandas`, `numpy`
- **Boosting:** `xgboost`, `catboost`
- **Serialization:** `joblib`

---

## 🚀 Quick Start (Inference)

To use the pre-trained model for prediction:

```python
import joblib
import pandas as pd

# 1. Load the Pipeline and Column Definition
model = joblib.load('ames_housing_super_model_production.pkl')
model_cols = joblib.load('ames_model_columns.pkl')

# 2. Define User Input (Can be partial data)
user_data = {
    "Neighborhood": "CollgCr",
    "LotArea": 9600,
    "OverallQual": 7,
    "YearBuilt": 2000
    # Missing columns will be auto-imputed
}

# 3. Align & Predict
input_df = pd.DataFrame([user_data]).reindex(columns=model_cols)
prediction = model.predict(input_df)[0]

print(f"Predicted Price: ${prediction:,.2f}")
```

---

## 🏆 Key Results

- **Metric: R^2 (Coefficient of Determination) on Test Data.**
- **Single Best Model (XGBoost): ~0.914**
- **Ensemble Model: 0.933 (~20% reduction in remaining error).**
- **Stress Test: Successfully handles extreme outliers (e.g., 200k sq ft inputs) without crashing or outputting infinity, thanks to tree-clamping and robust encoding.**

---

## 👨🏻‍💻 Author

Ozkan Gelincik — Data Scientist
🔗 LinkedIn: https://www.linkedin.com/in/ozkangelincik

