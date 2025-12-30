# Ames Housing Dashboard: Version History

## 🖥️ Project Overview
This module converts our static ROI analysis scripts into an interactive **web application** using **Python Shiny**.

The dashboard allows users to:
1.  **Configure a Base House:** Set neighborhood, square footage, quality, and age.
2.  **Toggle Renovations:** Instantly add/remove features (Garage, AC, Luxury Kitchen).
3.  **Simulate Deals:** Apply purchase discounts to see real-world "Flipper Profit."
4.  **Visualize ROI:** See real-time updates on Deal Economics via dynamic waterfall plots.

---

## 📂 Version History

### `dashboard.py` — The Prototype (MVP)
**"The Standalone Script"**

* **Goal:** Get the Shiny app running immediately to prove the interactive concept.
* **Key Characteristic:** The helper function `cast_to_str` (required by the model pipeline) was **manually defined** inside the script.
* **The "Hack":**
    ```python
    # Defined explicitly inside the file
    def cast_to_str(x):
        return x.astype(str)
    ```
* **Why we did this:** When loading a `.pkl` file, Python must be able to find all functions referenced inside it. By pasting the function directly into the script, we bypassed import errors during the initial testing phase.

### `dashboard_v2.py` — The Refactor
**"Production Ready Code"**

* **Goal:** Clean up the codebase and implement modular best practices.
* **Key Change:** Removed the manual function definition and imported it from a shared utility file.
* **The Fix:**
    ```python
    # Imported from the shared module
    from utils import cast_to_str
    ```
* **Why this is better:**
    * **DRY Principle (Don't Repeat Yourself):** We don't need to copy-paste the helper function into every new script we write.
    * **Maintainability:** If we ever change how `cast_to_str` works, we only update it in `utils.py`, and all apps update automatically.

### `dashboard_v3.py` — The Investor Edition (Final)
**"The Real World Simulator"**

* **Goal:** Move from simple renovation costs to realistic **Investment Economics**.
* **The Problem with v2:** It assumed you bought the house at full Retail Market Value, making almost every renovation look like a financial loss (Red Bar).
* **The Fix:** Added a **"Purchase Price Discount" Slider**.
* **New Logic:**
    * **Purchase Price:** `Fair Market Value * (1 - Discount%)`
    * **Net Profit:** `Final Sale Price - (Purchase Price + Renovation Cost)`
* **Visuals:** Added emojis (`🚀`, `📉`) and a stacked "Waterfall" plot to visualize the deal spread.
* **Key Insight:** This version proves that **"You make your money when you buy."** It allows users to simulate buying distressed properties (foreclosures) to find profitable deals.

---

## 🛠 Technical Deep Dive: The "Pickle Problem"

Why was `cast_to_str` such a big deal in v1 and v2?

1.  **The Serialized Pipeline:** Your `ames_housing_super_model_production.pkl` contains a `FunctionTransformer` that points to a function named `cast_to_str`.
2.  **The Loading Rule:** When `joblib.load()` runs, it looks for `cast_to_str` in the **current namespace**.
3.  **The Evolution:**
    * In **v1**, we forced it into the namespace by writing `def cast_to_str...`.
    * In **v2/v3**, we correctly imported it, which is the standard professional approach for deploying ML apps.

---

## 🏃 How to Run

**Run the final investor version (v3):**

```bash
shiny run --reload dashboard_v3.py
```
