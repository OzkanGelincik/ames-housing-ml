import requests

url = 'http://127.0.0.1:5000/predict'

base_house = {
    "Neighborhood": "NAmes",
    "GrLivArea": 1200,
    "OverallQual": 5,
    "YearBuilt": 1960
}

# 1. Get Base Price
print("1. Fetching Base Price...")
resp_base = requests.post(url, json=base_house)
price_base = resp_base.json()['predicted_price']
print(f"   Base Price: ${price_base:,.2f}")

# 2. Renovate (Kitchen Qual: Ex) and Add Garage
renovated_house = base_house.copy()
renovated_house['KitchenQual'] = 'Ex'  # Excellent Kitchen
renovated_house['GarageCars'] = 2      # 2-Car Garage

print("\n2. Renovating House (New Kitchen + Garage)...")
resp_reno = requests.post(url, json=renovated_house)
price_reno = resp_reno.json()['predicted_price']
print(f"   New Price:  ${price_reno:,.2f}")

# 3. Calculate Delta
delta = price_reno - price_base
print(f"\n📈 Value Added: ${delta:,.2f}")

if delta > 0:
    print("✅ Logic Check Passed: Renovations increased value.")
else:
    print("⚠️ Logic Check Warning: Value did not increase.")
