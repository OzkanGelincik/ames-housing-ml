# Ames Housing Renovation ROI Analysis: Version History

## 📌 Project Overview
This repository contains a series of Python scripts designed to simulate the financial return on investment (ROI) for various home renovations. 

Using a production-grade Machine Learning pipeline (**The Super Model**), these scripts:
1. **Create a "Digital Twin"** of a specific house profile (Base Case).
2. **Simulate specific renovations** (e.g., adding a garage, finishing a basement).
3. **Predict the new sale price** using the trained ensemble model.
4. **Calculate Value Lift and ROI** based on estimated costs.

---

## 📂 Version History & Evolution

### `analysis_roi_2.0.py` — The Prototype (MVP)
**"The Proof of Concept"**
* **Goal:** Establish the basic simulation loop and ensure the model pipeline could handle "What-If" scenarios.
* **Base House:** A synthetic, generic "Fixer Upper" created from dataset averages.
* **Key Feature:** Introduced the `renovations` dictionary structure and the `.copy()` logic to isolate experiments.
* **Limitation:** The base house was generic and didn't target a specific neighborhood strategy.

### `analysis_roi_3.0.py` — Context Awareness
**"The Neighborhood Strategy"**
* **Goal:** Test how **Location** impacts ROI.
* **Change:** Moved the simulation to **Northridge Heights (`NridgHt`)**, a high-value luxury neighborhood.
* **Key Insight:** This version demonstrated the "Penalty Principle." In a luxury neighborhood, *missing* a standard feature (like a garage or AC) penalizes the home value heavily. Therefore, adding these features yields a massive ROI compared to a cheaper neighborhood.

### `analysis_roi_4.0.py` — Realism & Data Integrity
**"The Realistic Baseline"**
* **Goal:** Fix logical inconsistencies in the data injection to improve prediction accuracy.
* **Critical Fix (`GarageYrBlt`):** * *Issue:* Previous versions added a garage but left the "Year Built" as 0. The model saw a "New Garage" built in the year 0 AD, which confused the algorithm.
    * *Fix:* Explicitly set `GarageYrBlt` to match the house's construction year (2005).
* **Scenario:** Scenario C (Clean & Realistic). A modern 2005 build stripped of amenities, representing a realistic "distressed asset."
* **Pricing Model:** Retail Pricing (Standard Homeowner costs).

### `analysis_roi_5.0.py` — The Investor Pivot
**"The Flipper's Perspective"**
* **Goal:** Simulate the economics for a Professional Investor vs. a Regular Homeowner.
* **Change:** Adjusted the **Cost Basis** to represent "Investor Pricing" (Wholesale/DIY/Contractor Rates).
    * *Retail Cost (v4.0):* High costs, lower ROI.
    * *Investor Cost (v5.0):* ~30-50% lower costs, significantly higher ROI.
* **Key Insight:** Proves why flipping is profitable for pros but risky for homeowners. The "Value Lift" remains the same as v4.0, but the lower denominator (Cost) skyrockets the ROI.

### `dashboard.py` — The Interactive App
**"The User Interface"**
* **Goal:** Convert the static scripts into a dynamic Python Shiny web application.
* **Features:** * Interactive sliders for Square Footage and Quality.
    * Real-time toggles for adding/removing amenities (Garage, AC, Kitchen).
    * Live ROI calculation and visualization using Matplotlib.

---

## 🛠 Setup & Usage

### 1. Prerequisites
Ensure you have the trained model artifacts in a `models/` directory relative to these scripts:
* `ames_housing_super_model_production.pkl` (The Pipeline)
* `ames_model_columns.pkl` (Column alignment)
* `ames_model_defaults.pkl` (Imputation values)

### 2. How to Run
Run any version directly from your terminal or IDE:

```bash
# Run the Investor Analysis
python analysis_roi_5.0.py

# Run the Dashboard App
shiny run dashboard.py
```

###3. Customizing Scenarios

To test your own scenarios, modify the renovations dictionary inside any script:

```bash
renovations = {
    "My New Experiment": {
        "changes": { "PoolQC": "Ex", "PoolArea": 500 },
        "cost": 30000
    }
}
```

### 📊 Summary of Results

| Version | Scenario | Pricing Model | Key Finding |
| :--- | :--- | :--- | :--- |
| **v2.0** | Generic | Retail | The simulation loop works. |
| **v3.0** | Luxury (`NridgHt`) | Retail | Location drives the "ceiling" of value add. |
| **v4.0** | Realistic (`NridgHt`) | Retail | Data integrity (dates, valid types) is crucial for accurate predictions. |
| **v5.0** | Realistic (`NridgHt`) | **Investor** | Lowering costs is the most effective lever for increasing ROI. |































































