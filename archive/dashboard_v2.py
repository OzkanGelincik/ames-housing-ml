from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
from utils import cast_to_str  # <--- The Hero of the story

# ==========================================
# 1. LOAD ASSETS
# ==========================================
# DELETE the manual definition of cast_to_str you added earlier.

# --- CHANGE IS HERE ---
# 1. DELETE the manual "def cast_to_str..." block if it's still there.
# 2. ADD this import line: (ADDED ABOVE!)
# from utils import cast_to_str
# ----------------------

# Load the model and metadata
MODELS_DIR = Path(__file__).parent / "models"

model = joblib.load(MODELS_DIR / 'ames_housing_super_model_production.pkl')
model_columns = joblib.load(MODELS_DIR / 'ames_model_columns.pkl')
model_defaults = joblib.load(MODELS_DIR / 'ames_model_defaults.pkl')

# Extract options for dropdowns
# (Logic: Try to get list from defaults; if strictly a list, use it. Otherwise fallback to hardcoded top neighborhoods)
neighborhoods = sorted(list(set(model_defaults.get('Neighborhood', [])) if isinstance(model_defaults.get('Neighborhood'), list) else ["NridgHt", "NoRidge", "StoneBr", "OldTown", "NAmes", "Edwards", "CollgCr"]))

# ==========================================
# 2. UI LAYOUT
# ==========================================
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("🏠 House Flipper"),
        ui.hr(),
        ui.h5("1. Base House Config"),
        ui.input_select("neighborhood", "Neighborhood", choices=neighborhoods, selected="NridgHt"),
        ui.input_slider("sqft", "Living Area (SqFt)", min=500, max=4000, value=2000),
        ui.input_slider("quality", "Overall Quality (1-10)", min=1, max=10, value=7),
        ui.input_numeric("year_built", "Year Built", value=2005),

        ui.hr(),
        ui.h5("2. Renovations (Simulate)"),
        ui.input_switch("add_garage", "Add 2-Car Garage (Cost: $20k)", value=False),
        ui.input_switch("add_ac", "Add Central Air (Cost: $6k)", value=False),
        ui.input_switch("reno_kitchen", "Luxury Kitchen (Cost: $25k)", value=False),
        ui.input_switch("finish_bsmt", "Finish Bsmt (+500sf, $30k)", value=False),
    ),

    ui.layout_columns(
        ui.card(
            ui.card_header("💰 Predicted Sale Price"),
            ui.output_ui("price_box"),
        ),
        ui.card(
            ui.card_header("📈 Value Added (Lift)"),
            ui.output_ui("lift_box"),
        ),
    ),
    ui.card(
        ui.card_header("Return on Investment (ROI) Analysis"),
        ui.output_plot("roi_plot"),
    ),
)

# ==========================================
# 3. SERVER LOGIC
# ==========================================
def server(input, output, session):

    @reactive.Calc
    def calculate_metrics():
        # --- A. CREATE BASE HOUSE ---
        # Start with defaults
        base_df = pd.DataFrame([model_defaults])

        # Override with UI inputs
        base_df['Neighborhood'] = input.neighborhood()
        base_df['GrLivArea'] = input.sqft()
        base_df['OverallQual'] = input.quality()
        base_df['YearBuilt'] = input.year_built()

        # Set "Bad" defaults for the renovation targets so we can simulate adding them
        # If the switch is OFF, we assume the house DOES NOT have it.
        # If the switch is ON, we assume the house HAS it.

        # 1. Garage Logic
        if input.add_garage():
            base_df['GarageCars'] = 2
            base_df['GarageArea'] = 576
            base_df['GarageType'] = 'Attchd'
            base_df['GarageYrBlt'] = input.year_built() # Assume built same time
        else:
            base_df['GarageCars'] = 0
            base_df['GarageArea'] = 0
            base_df['GarageType'] = 'None'

        # 2. AC Logic
        base_df['CentralAir'] = 'Y' if input.add_ac() else 'N'

        # 3. Kitchen Logic
        base_df['KitchenQual'] = 'Ex' if input.reno_kitchen() else 'TA'

        # 4. Basement Logic
        # Start with a standard unfinished basement
        base_df['TotalBsmtSF'] = 1000
        base_df['BsmtFinSF1'] = 0
        if input.finish_bsmt():
            base_df['BsmtFinSF1'] = 500 # Add finished area

        # Align columns
        final_df = base_df.reindex(columns=model_columns).fillna(model_defaults)

        # PREDICT CURRENT PRICE
        current_price = model.predict(final_df)[0]

        # --- B. CALCULATE BASELINE (NO RENOVATIONS) ---
        # To get "Lift", we need to know what the price WOULD be without the active switches
        # This is a bit tricky dynamically, so let's simplify:
        # We calculate the "Cost" based on active switches.

        total_cost = 0
        if input.add_garage(): total_cost += 20000
        if input.add_ac(): total_cost += 6000
        if input.reno_kitchen(): total_cost += 25000
        if input.finish_bsmt(): total_cost += 30000

        return current_price, total_cost

    @output
    @render.ui
    def price_box():
        price, cost = calculate_metrics()
        return ui.h1(f"${price:,.0f}")

    @output
    @render.ui
    def lift_box():
        # This is a simplified view. Ideally, we run two predictions (Base vs Renovated)
        # But for UI speed, let's just show the Cost vs Price implication
        price, cost = calculate_metrics()

        # We need a baseline to compare against.
        # Let's run a quick "Pre-Reno" prediction
        base_df = pd.DataFrame([model_defaults])
        base_df['Neighborhood'] = input.neighborhood()
        base_df['GrLivArea'] = input.sqft()
        base_df['OverallQual'] = input.quality()
        base_df['YearBuilt'] = input.year_built()

        # Force "No Renovation" state
        base_df['GarageCars'] = 0
        base_df['GarageArea'] = 0
        base_df['CentralAir'] = 'N'
        base_df['KitchenQual'] = 'TA'
        base_df['BsmtFinSF1'] = 0
        base_df['TotalBsmtSF'] = 1000

        final_base = base_df.reindex(columns=model_columns).fillna(model_defaults)
        baseline_price = model.predict(final_base)[0]

        lift = price - baseline_price

        color = "text-success" if lift > cost else "text-danger"
        return ui.div(
            ui.h3(f"+${lift:,.0f}", class_=color),
            ui.p(f"Renovation Cost: ${cost:,.0f}")
        )

    @output
    @render.plot
    def roi_plot():
        price, cost = calculate_metrics()

        # Recalculate baseline for the plot
        base_df = pd.DataFrame([model_defaults])
        base_df['Neighborhood'] = input.neighborhood()
        base_df['GrLivArea'] = input.sqft()
        base_df['OverallQual'] = input.quality()
        base_df['YearBuilt'] = input.year_built()
        base_df['GarageCars'] = 0; base_df['GarageArea'] = 0
        base_df['CentralAir'] = 'N'; base_df['KitchenQual'] = 'TA'
        base_df['BsmtFinSF1'] = 0; base_df['TotalBsmtSF'] = 1000

        final_base = base_df.reindex(columns=model_columns).fillna(model_defaults)
        baseline_price = model.predict(final_base)[0]

        lift = price - baseline_price

        # Data for plotting
        categories = ['Base Value', 'Renovation Cost', 'Profit/Loss']
        values = [baseline_price, cost, (lift - cost)]
        colors = ['gray', 'blue', 'green' if (lift-cost) > 0 else 'red']

        fig, ax = plt.subplots(figsize=(5, 3))
        ax.barh(categories, values, color=colors)
        ax.set_title(f"Deal Economics (Total Value: ${price:,.0f})")

        # Add labels
        for i, v in enumerate(values):
            ax.text(v, i, f" ${v:,.0f}", va='center')

        return fig

app = App(app_ui, server)
