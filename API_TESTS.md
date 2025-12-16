# The Detailed Version
**Destination:** Create a new file named **`API_TESTS.md`**.
*Purpose: Detailed documentation and source code for your testing suite.*


# 🛠️ API Testing Suite

This document outlines the testing protocols for the Ames Housing Prediction API (`app_3.0.py`). These scripts verify connectivity, input validation, outlier handling, and business logic.

## 📋 Prerequisites

1. **Start the API Server** in a separate terminal window:
   ```bash
   python app_3.0.py
   ```

2. Install Request Library (if not already installed):

```bash
pip install requests
```

# Tests

1. Connectivity Test (`test_basic.py`)

Objective: Verify that the "Happy Path" works. This script sends a partial JSON payload (simulating a lazy user) and checks if the API successfully imputes missing values and returns a price.

```python
import requests
import json

url = '[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)'

# Standard house with partial data
house_data = {
    "Neighborhood": "CollgCr",
    "GrLivArea": 1500,
    "YearBuilt": 2005,
    "OverallQual": 7,
    "GarageCars": 2
}

print(f"Sending request for: {house_data}")

try:
    response = requests.post(url, json=house_data)
    if response.status_code == 200:
        result = response.json()
        print("\n✅ SUCCESS!")
        print(f"Predicted Price: ${result['predicted_price']:,.2f}")
        print(f"Server Version:  {result['version']}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Connection Refused. Is app_3.0.py running?")
```

2. Safety & Stress Test (`test_guardrails.py`)

Objective: Ensure the system is "Fail-Safe."

- Imputation: Can it handle a request with only 1 feature?
- Clamping: Does it prevent runaway predictions for extreme outliers (e.g., 200,000 sq ft)?
- Unknown Categories: Does it crash if a user enters a Neighborhood that doesn't exist?

```python
import requests

url = '[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)'

def send_test(name, data):
    print(f"\n--- TEST: {name} ---")
    resp = requests.post(url, json=data)
    if resp.status_code == 200:
        price = resp.json()['predicted_price']
        print(f"💰 Price: ${price:,.2f}")
    else:
        print("❌ Failed")

# TEST A: The Mega Mansion (Should be clamped to ~10k sq ft price)
send_test("Mega Mansion (200k SqFt)", {
    "GrLivArea": 200000,
    "OverallQual": 10,
    "Neighborhood": "NoRidge"
})

# TEST B: The Minimalist (Only providing 1 feature)
send_test("Minimalist (Only LotArea provided)", {
    "LotArea": 5000
})

# TEST C: The Unknown Category (Should default to 'None' internally)
send_test("Unknown Category", {
    "Neighborhood": "MarsBase",
    "GrLivArea": 1000
})
```

3. Logic & Sensitivity Test (`test_comparison.py`)

Objective: Verify that the model aligns with economic reality.

Hypothesis: A house with an Excellent Kitchen and a Garage must cost more than the exact same house without them.

```python
import requests

url = '[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)'

base_house = {
    "Neighborhood": "NAmes",
    "GrLivArea": 1200,
    "OverallQual": 5,
    "YearBuilt": 1960
}

# 1. Get Base Price
resp_base = requests.post(url, json=base_house)
price_base = resp_base.json()['predicted_price']
print(f"Base Price: ${price_base:,.2f}")

# 2. Renovate
renovated_house = base_house.copy()
renovated_house['KitchenQual'] = 'Ex'  # Upgrade Kitchen
renovated_house['GarageCars'] = 2      # Add Garage

resp_reno = requests.post(url, json=renovated_house)
price_reno = resp_reno.json()['predicted_price']
print(f"New Price:  ${price_reno:,.2f}")

# 3. Validation
delta = price_reno - price_base
print(f"Value Added: ${delta:,.2f}")

if delta > 0:
    print("✅ Logic Check Passed")
else:
    print("⚠️ Logic Check Warning: Value did not increase")
```





























