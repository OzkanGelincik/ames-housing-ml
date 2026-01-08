from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
from utils import cast_to_str

# ==========================================
# 1. LOAD ASSETS
# ==========================================
MODELS_DIR = Path(__file__).parent / "models"

model = joblib.load(MODELS_DIR / 'ames_housing_super_model_production.pkl')
model_columns = joblib.load(MODELS_DIR / 'ames_model_columns.pkl')
model_defaults = joblib.load(MODELS_DIR / 'ames_model_defaults.pkl')
# Load the new options file
model_options = joblib.load(MODELS_DIR / 'ames_model_options.pkl')

# Get the full list (No more guessing or hardcoding!)
neighborhoods = model_options['Neighborhood']

# ==========================================
# 2. UI LAYOUT
# ==========================================
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3("🏠 House Flipper Pro"),
        ui.hr(),
        ui.h5("1. Acquisition Strategy"),
        ui.input_select("neighborhood", "Neighborhood", choices=neighborhoods, selected="NAmes"),
        ui.input_slider("sqft", "Living Area (SqFt)", min=500, max=4000, value=1500),
        ui.input_slider("quality", "Current Quality (1-10)", min=1, max=10, value=5),
        ui.input_numeric("year_built", "Year Built", value=1960),
        # NEW: The Discount Slider
        ui.input_slider("discount", "Purchase Discount (%)", min=0, max=50, value=0, post="%"),
        ui.help_text("Simulate buying below market value (e.g., foreclosure, distress)."),

        ui.hr(),
        ui.h5("2. Renovation Plan"),
        ui.input_switch("add_garage", "Add 2-Car Garage (Cost: $20k)", value=False),
        ui.input_switch("add_ac", "Add Central Air (Cost: $6k)", value=False),
        ui.input_switch("reno_kitchen", "Luxury Kitchen (Cost: $25k)", value=False),
        ui.input_switch("finish_bsmt", "Finish Bsmt (+500sf, $30k)", value=False),
    ),

    ui.layout_columns(
        ui.card(
            ui.card_header("💰 Deal Economics"),
            ui.output_ui("economics_box"),
        ),
        ui.card(
            ui.card_header("📈 Net Profit Potential"),
            ui.output_ui("profit_box"),
        ),
    ),
    ui.card(
        ui.card_header("ROI Analysis (Purchase + Reno vs. Sale)"),
        ui.output_plot("roi_plot"),
    ),
)

# ==========================================
# 3. SERVER LOGIC
# ==========================================
def server(input, output, session):

    @reactive.Calc
    def calculate_deal():
        # --- A. DEFINE BASE HOUSE ---
        base_df = pd.DataFrame([model_defaults])
        base_df['Neighborhood'] = input.neighborhood()
        base_df['GrLivArea'] = input.sqft()
        base_df['OverallQual'] = input.quality()
        base_df['YearBuilt'] = input.year_built()
        
        # Force "No Renovation" state for the baseline
        # We need this to calculate the "Fair Market Value" BEFORE you touch it
        base_no_reno = base_df.copy()
        base_no_reno['GarageCars'] = 0; base_no_reno['GarageArea'] = 0

        base_no_reno['GarageType'] = 'None'  # <--- match the renovation logic

        base_no_reno['CentralAir'] = 'N'
        base_no_reno['KitchenQual'] = 'TA'
        base_no_reno['BsmtFinSF1'] = 0; base_no_reno['TotalBsmtSF'] = 1000
        
        final_base = base_no_reno.reindex(columns=model_columns).fillna(model_defaults)
        fmv_pre_reno = model.predict(final_base)[0]

        # --- B. APPLY PURCHASE DISCOUNT ---
        discount_pct = input.discount() / 100
        purchase_price = fmv_pre_reno * (1 - discount_pct)

        # --- C. APPLY RENOVATIONS ---
        reno_df = base_df.copy()
        
        # 1. Garage Logic
        if input.add_garage():
            reno_df['GarageCars'] = 2
            reno_df['GarageArea'] = 576
            reno_df['GarageType'] = 'Attchd'
            reno_df['GarageYrBlt'] = input.year_built()
        else:
            reno_df['GarageCars'] = 0
            reno_df['GarageArea'] = 0
            reno_df['GarageType'] = 'None'

        # 2. AC Logic
        reno_df['CentralAir'] = 'Y' if input.add_ac() else 'N'

        # 3. Kitchen Logic
        reno_df['KitchenQual'] = 'Ex' if input.reno_kitchen() else 'TA'

        # 4. Basement Logic
        reno_df['TotalBsmtSF'] = 1000
        reno_df['BsmtFinSF1'] = 0
        if input.finish_bsmt():
            reno_df['BsmtFinSF1'] = 500

        final_reno = reno_df.reindex(columns=model_columns).fillna(model_defaults)
        
        # PREDICT FINAL SALE PRICE
        sale_price = model.predict(final_reno)[0]

        # --- D. CALCULATE COSTS ---
        reno_cost = 0
        if input.add_garage(): reno_cost += 20000
        if input.add_ac(): reno_cost += 6000
        if input.reno_kitchen(): reno_cost += 25000
        if input.finish_bsmt(): reno_cost += 30000

        return purchase_price, reno_cost, sale_price, fmv_pre_reno

    @output
    @render.ui
    def economics_box():
        purchase, cost, sale, fmv = calculate_deal()
        total_investment = purchase + cost
        return ui.div(
            ui.p(f"Purchase Price: ${purchase:,.0f} (FMV: ${fmv:,.0f})"),
            ui.p(f"Reno Cost: ${cost:,.0f}"),
            ui.hr(style="margin: 5px 0"),
            ui.h4(f"Total Invested: ${total_investment:,.0f}"),
            ui.h5(f"Est. Sale Price: ${sale:,.0f}", style="color: blue")
        )

    @output
    @render.ui
    def profit_box():
        purchase, cost, sale, fmv = calculate_deal()
        net_profit = sale - (purchase + cost)
        
        color = "text-success" if net_profit > 0 else "text-danger"
        emoji = "🚀" if net_profit > 0 else "📉"
        
        return ui.div(
            ui.h2(f"{emoji} ${net_profit:,.0f}", class_=color),
            ui.p(f"Return on Investment: {(net_profit / (purchase+cost))*100:.1f}%")
        )

    @output
    @render.plot
    def roi_plot():
        purchase, cost, sale, fmv = calculate_deal()
        net_profit = sale - (purchase + cost)

        # Plotting
        categories = ['Total Investment', 'Sale Price']
        values = [purchase + cost, sale]
        colors = ['gray', 'green' if net_profit > 0 else 'red']

        fig, ax = plt.subplots(figsize=(6, 3))
        
        # Stacked bar for Investment (Purchase + Reno)
        ax.barh(['Investment'], [purchase], label='Purchase Price', color='lightblue')
        ax.barh(['Investment'], [cost], left=[purchase], label='Reno Cost', color='orange')
        
        # Bar for Sale Price
        ax.barh(['Exit Strategy'], [sale], color='lightgreen')

        # Add profit/loss line
        ax.axvline(x=purchase+cost, color='black', linestyle='--', alpha=0.5)
        
        ax.set_title(f"Deal Waterfall (Net: ${net_profit:,.0f})")
        ax.legend()
        
        # Add text labels
        ax.text(purchase/2, 0, f"${purchase/1000:.0f}k", va='center', ha='center')
        if cost > 0:
            ax.text(purchase + cost/2, 0, f"${cost/1000:.0f}k", va='center', ha='center')
        ax.text(sale, 1, f" ${sale:,.0f}", va='center')

        return fig

app = App(app_ui, server)
if __name__ == "__main__":
    app.run()
