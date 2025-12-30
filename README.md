# 🏡 Ames Housing Price Prediction: Ensemble Architecture

### 🚀 **Test R² Score: 0.933**

This repository contains a robust machine learning pipeline designed to predict housing prices in Ames, Iowa. It utilizes a **Weighted Voting Ensemble** combining Linear Models (Lasso) and Gradient Boosted Trees (XGBoost, CatBoost) to achieve high accuracy while maintaining interpretability and safety against outliers.

---

## 📂 Repository Structure

This project is divided into three distinct phases:

### 1. 🔬 The Lab Notebook (`ames_housing_prices_modeling_master.ipynb`)
**"The Research Phase"**
- Extensive Exploratory Data Analysis (EDA).
- Model training: OLS, Ridge, Lasso, ElasticNet, SVR, Random Forest, XGBoost, CatBoost, and Voting (Ensemble) Regressors.
- Feature Engineering experiments (Ordinal vs. One-Hot Encoding).
- Hyperparameter tuning via GridSearch.
- Stress Testing (e.g., 'Ghost House', 'Impossible House', and 'Mega-Mansion' simulations).
- Feature Importance Analysis (SHAP values, Permutation Importance).

### 2. 🏭 The Production Notebook (`ames_housing_prices_modeling_production.ipynb`)
**"The Deployment Phase"**
- A streamlined execution pipeline (incl. the winning model 🏆).
- Consolidates preprocessing and modeling into a single `sklearn` Pipeline.
- Handles raw user input with automatic imputation using `ames_model_defaults.pkl`.
- Generates deployment artifacts (`.pkl` files) synchronized with the dashboard.

### 3. 🖥️ The Interactive Dashboard (`dashboard_v3.py`)
**"The Investor Interface"**
- A live web application built with **Shiny for Python**.
- **Investor Mode:** Simulate purchasing distressed properties at a discount (0-50%).
- **Flipper Mode:** Toggle renovations (Luxury Kitchen, Finished Basement, Central Air) and visualize real-time ROI.
- **Deal Economics:** Dynamic waterfall charts showing "Total Investment" vs. "Exit Price."

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

- **Core:** `scikit-learn`, `pandas`, `numpy`, `joblib`
- **Boosting:** `xgboost`, `catboost`
- **Dashboard:** `shiny`, `rsconnect-python`, `matplotlib`
- **Utilities:** Custom `utils.py` module for robust data casting.

---

## 🚀 Quick Start

### 1. Run the Dashboard (UI)
To launch the interactive deal simulator locally:

```bash
shiny run --reload dashboard_v3.py
```

### 2. Run Inference (Python API)

To use the pre-trained model for code-based prediction:

``` python
import joblib
import pandas as pd
from utils import cast_to_str # Helper for pipeline compatibility

# 1. Load the Pipeline and Artifacts
model = joblib.load('models/ames_housing_super_model_production.pkl')
model_cols = joblib.load('models/ames_model_columns.pkl')

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

## 🧪 Verification & Testing

| Script | Purpose |
| :--- | :--- |
| **`test_basic.py`** | **Connectivity Check.** Sends a standard request to ensure the API returns a valid price. |
| **`test_guardrails_v2.py`** | **Safety Check.** Stress tests the system with extreme inputs (e.g., 200k sq ft mansions) to ensure stability. |
| **`test_comparison.py`** | **Logic Check.** Compares a standard house vs. a renovated house to ensure the model responds logically to improvements (Price increases). |

---

## 🏆 Key Results

- **Metric: R^2 (Coefficient of Determination) on Test Data.**
- **Single Best Model (XGBoost): ~0.914**
- **Ensemble Model: 0.933 (~20% reduction in remaining error).**
- **Stress Test: Successfully handles extreme outliers (e.g., 200k sq ft inputs) without crashing or outputting infinity, thanks to tree-clamping and robust encoding.**
- **Business Impact: The "Buy Box" strategy derived from SHAP analysis identifies that finishing a basement and upgrading a kitchen yields the highest ROI, while "Garage Type" is a low-leverage renovation.**

---

## 👨🏻‍💻 Author

Ozkan Gelincik — Data Scientist
🔗 LinkedIn: https://www.linkedin.com/in/ozkangelincik

