# 🧪 Lab Notebook: Research & Experimentation

**File:** `ames_housing_prices_modeling_master.ipynb`

This notebook serves as the "Research Lab" for the Ames Housing project. It documents the iterative process of data cleaning, feature selection, and model tuning that led to the final architecture.

## 🎯 Objectives
1.  **Data Cleaning:** Establish a strategy for handling 79 different features with varying degrees of missingness.
2.  **Encoding Strategy:** Determine which models perform best with One-Hot Encoding vs. Ordinal Encoding.
3.  **Redundancy Removal:** Test the impact of removing highly correlated features (Lasso vs. Trees).

## 🔍 Key Experiments

### 1. The "Dual-Encoding" Discovery
We found that Linear models (Lasso) require **One-Hot Encoding** to function correctly, while Tree models (XGBoost/CatBoost) perform significantly better (and faster) with **Ordinal (Integer) Encoding**.
* *Solution:* The final ensemble uses a bifurcated pipeline where data is processed differently depending on the model branch.

### 2. Feature Redundancy
* **Finding:** A `CorrelationThreshold` of 0.9 detected ~28 redundant features in One-Hot data, but 0 in Ordinal data.
* *Decision:* We removed the redundancy filter for the Tree models (safe pass-through) but implicitly allowed Lasso to handle its own regularization.

### 3. Stress Testing (The "Ghost" & "Mansion")
We subjected the model to extreme synthetic inputs to test stability:
* **The Ghost House:** 0 SqFt, 0 Quality. -> Result: Logical low price (Lot Value).
* **The Mega Mansion:** 200,000 SqFt. -> Result: Safe prediction (~$240k).
    * *Insight:* Pure Linear models crashed (predicted Infinity). The Ensemble survived because the Tree models "clamped" the prediction, and the Encoder zeroed out the unseen massive value for the Linear model.

## 📊 Feature Importance
Permutation importance analysis revealed that while **OverallQual** and **GrLivArea** are the dominant drivers, the Ensemble gains its edge by effectively utilizing "minor" features that single models often ignore.

## ⚙️ How to Use
Use this notebook to:
- Re-run GridSearches for hyperparameters.
- Visualize feature correlations.
- Understand the "Why" behind the architectural decisions in the Production notebook.
