# 🏗️ API Evolution & Version History

This repository contains several iterations of the Ames Housing Price Prediction API. The project evolved from a basic Flask wrapper to a robust, production-grade system with strict validation and guardrails.

### 🚀 Recommendation
**Use `app_4.0.py` for all testing and production use cases.** It contains the full Scikit-Learn pipeline, smart imputation for missing data, and Pydantic-based input validation.

---

## 📜 Version History

### 🟢 `app_4.0.py` (Current Production Build)
* **Status:** ✅ **Recommended**
* **Key Feature:** **Strict Input Validation (Pydantic)**
* **Description:** This version introduces "Fail Fast" logic. Instead of quietly fixing bad data (like a 200,000 sq ft house), it rejects invalid requests with a `400 Bad Request` error. It uses `Pydantic` to define a strict schema for inputs.
* **Capabilities:**
    * Validates data types and ranges before the model sees them.
    * Supports a "Renovation Calculator" via optional fields (e.g., specific inputs for `KitchenQual` or `GarageCars`).
    * Uses the full `Pipeline` to handle categorical encoding automatically.

### 🟡 `app_3.0.py` (The Pipeline Upgrade)
* **Status:** ⚠️ Deprecated
* **Key Feature:** **Full Scikit-Learn Pipeline Integration**
* **Description:** This version fixed the "Raw Data" crash. It switched from loading just the model to loading the full `Pipeline` (Preprocessor + Model). It correctly handles categorical string data (e.g., "CollgCr") by routing it through the saved encoders.
* **Limitation:** It still accepted nonsensical data (e.g., massive square footage) and tried to predict a price for it, leading to "silent failures."

### 🟠 `app_2.0.py` (Smart Imputation)
* **Status:** ❌ Deprecated
* **Key Feature:** **Handling Missing Data**
* **Description:** This version introduced `model_defaults.pkl`. If a user didn't provide a specific feature (like `GarageCars`), the app automatically filled it with the median/mode from the training set instead of crashing.
* **Limitation:** It relied on the old model file and lacked proper categorical encoding support.

### 🔴 `app.py` (The MVP)
* **Status:** ❌ Deprecated
* **Key Feature:** **Proof of Concept**
* **Description:** The initial Minimum Viable Product. It proved we could serve predictions via Flask.
* **Limitation:** Highly fragile. It filled missing data with `0` (which is statistically dangerous) and crashed easily on invalid inputs.

---

## 🛠️ Quick Start (App 4.0)

### 1. Install Requirements
Ensure you have the necessary libraries, including Pydantic.
```bash
pip install flask pandas scikit-learn xgboost pydantic
```

### 2. Run the Server

```bash
python app_4.0.py
```

### 3. Send a Test Request

You can use curl or Python requests.

Valid Request (Returns Price):

```bash
curl -X POST [http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict) \
     -H "Content-Type: application/json" \
     -d '{"Neighborhood": "CollgCr", "GrLivArea": 1500, "YearBuilt": 2005, "OverallQual": 7}'
```

Invalid Request (Returns 400 Error):

```bash
# This will fail because 200,000 sq ft is out of bounds
curl -X POST [http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict) \
     -H "Content-Type: application/json" \
     -d '{"Neighborhood": "NoRidge", "GrLivArea": 200000, "YearBuilt": 2000, "OverallQual": 10}'
```

## 📊 Comparison: Why App 4.0?

| Feature | App 3.0 | App 4.0 (Recommended) |
| :--- | :--- | :--- |
| **Input Validation** | Manual `if` statements (weak) | **Pydantic Schema** (strict & auto-doc) |
| **Bad Data Handling** | Silently processes it (Dangerous) | **Returns 400 Error** (Safe) |
| **Missing Fields** | Fills with defaults | Fills with defaults (but strictly typed) |
| **Developer Experience** | Hard to debug silent errors | Clear error messages (e.g., "Field required") |
























