# 🏭 Production Notebook: Pipeline & Deployment

**File:** `ames_housing_prices_modeling_production.ipynb`

This notebook contains the optimized, streamlined code meant for deployment. It strips away the research code (grid searches, plots) and focuses on defining, training, and saving the final inference pipeline.

## 📦 The "Grand Pipeline"

The entire preprocessing and modeling logic is wrapped in a single Scikit-Learn `Pipeline` object. This ensures that **no data leakage** occurs and that all transformations applied to training data are automatically applied to new data.

### Pipeline Steps:
1.  **Input:** Raw DataFrame (Strings & Numbers).
2.  **Preprocessing (ColumnTransformer):**
    * *Categorical:* Cast to String -> Impute "None" -> Ordinal Encoder.
    * *Numerical:* Impute Median.
3.  **Target Transformation:** `np.log1p` (Log Price) to normalize error distribution.
4.  **Voting Regressor:**
    * Branch A: Lasso (Internal One-Hot Encoding).
    * Branch B: XGBoost.
    * Branch C: CatBoost.
5.  **Output:** `np.expm1` (Real Dollar Price).

## 💾 Generated Artifacts

Running this notebook produces the following files needed for the API/App:

| File | Description |
| :--- | :--- |
| `ames_housing_super_model_production.pkl` | The serialized Pipeline (Brain + Translator). Size: ~2-5MB. |
| `ames_model_columns.pkl` | A list of the 79 training columns. Used for aligning user input. |

## 🔌 Inference Logic (The "Bridge")

A critical component of this notebook is the **Reindexing Bridge**.
Because Scikit-Learn pipelines expect a fixed shape, partial user inputs (e.g., missing "GarageArea") must be padded with `NaN` before prediction.

**Snippet for Deployment:**
```python
# Force input to match training structure
expected_cols = joblib.load('ames_model_columns.pkl')
input_df = pd.DataFrame([user_input]).reindex(columns=expected_cols)
```
