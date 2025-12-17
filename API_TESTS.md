# The Detailed Version
**Destination:** Create a new file named **`API_TESTS.md`**.
*Purpose: Detailed documentation and source code for your testing suite.*


# 🛠️ API Testing Suite

This document outlines the testing protocols for the Ames Housing Prediction API (`app_3.0.py`). These scripts verify connectivity, input validation, outlier handling, and business logic.

## 📋 Prerequisites

1. **Start the API Server** in a separate terminal window:
   ```bash
   python app_4.0.py
   ```

2. Install Request Library (if not already installed):

```bash
pip install requests
```

# Tests

1. Connectivity Test (`test_basic.py`)

Objective: Verify the "Happy Path." The server should return a price and the Version 4.0 tag.

```python
import requests
import json

url = '[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)'

# Standard house with valid data
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
        print(f"💰 Predicted Price: ${result['predicted_price']:,.2f}")
        print(f"ℹ️  Server Version:  {result.get('version', 'Unknown')}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
except Exception as e:
    print(f"❌ Connection Refused. Is app_4.0.py running?")
```

2. Safety & Stress Test (`test_guardrails_v2.py`)

Objective: Verify "Fail-Fast" behavior. The system must block invalid inputs.

- Success Condition: Receiving a `400 Bad Request` for bad data.
- Failure Condition: Receiving a `200 OK` (Price) for bad data.

```python
import requests

BASE_URL = "[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)"

def test_request(name, data):
    print(f"\n--- TEST: {name} ---")
    print(f"Input: {data}")

    try:
        response = requests.post(BASE_URL, json=data)

        # SCENARIO 1: Success (200 OK) - We expected a price
        if response.status_code == 200:
            result = response.json()
            print(f"💰 Price: ${result['predicted_price']:,.2f}")

        # SCENARIO 2: Guardrail Blocked It (400 Bad Request) - EXPECTED FOR BAD DATA
        elif response.status_code == 400:
            error_data = response.json()
            print("✅ GUARDRAIL ACTIVE: Request Blocked.")
            if 'details' in error_data:
                print(f"   Reason: {error_data['details'][0]['msg']}")
                print(f"   Field:  {error_data['details'][0]['loc']}")

        # SCENARIO 3: Server Crash (500)
        else:
            print(f"❌ SERVER ERROR ({response.status_code}): {response.text}")

    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

# RUN TESTS
# 1. Mega Mansion (Should Fail: >10,000 sq ft)
test_request("Mega Mansion", {'GrLivArea': 200000, 'OverallQual': 10, 'Neighborhood': 'NoRidge', 'YearBuilt': 2000})

# 2. Minimalist (Should Fail: Missing Required Fields)
test_request("Minimalist", {'LotArea': 5000})

# 3. Valid House (Should Succeed)
test_request("Standard House", {'Neighborhood': 'CollgCr', 'GrLivArea': 1500, 'YearBuilt': 2005, 'OverallQual': 7})
```

3. Renovation ROI Test (`test_comparison.py`)

Objective: Verify that adding "Optional" fields (Kitchen Quality, Garage) correctly increases the price.

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
print("1. Fetching Base Price...")
resp_base = requests.post(url, json=base_house)
price_base = resp_base.json()['predicted_price']
print(f"   Base Price: ${price_base:,.2f}")

# 2. Renovate (Add Optional Pydantic Fields)
print("\n2. Renovating House (New Kitchen + Garage)...")
renovated_house = base_house.copy()
renovated_house['KitchenQual'] = 'Ex'  # Excellent Kitchen
renovated_house['GarageCars'] = 2      # 2-Car Garage

resp_reno = requests.post(url, json=renovated_house)
price_reno = resp_reno.json()['predicted_price']
print(f"   New Price:  ${price_reno:,.2f}")

# 3. Validation
delta = price_reno - price_base
print(f"\n📈 Value Added: ${delta:,.2f}")

if delta > 1000:
    print("✅ Logic Check Passed: Renovations increased value.")
else:
    print("⚠️ Logic Check Warning: Value increase was minimal.")
```

# 🟡 Part 2: Legacy Testing (app_3.0.py)
Status: Deprecated ⚠️ Behavior: Permissive. Attempts to fix bad data silently. Note: If `app_3.0.py` is in the `archive/`` folder, you must move it to the root directory to run these tests (so it can find the `models/`` folder).

1. Start the Legacy Server

```bash
python app_3.0.py
```

2. Guardrails Test (Legacy Behavior)

Objective: Demonstrate "Silent Failure." The system accepts invalid inputs and returns a price.

```python
import requests

url = '[http://127.0.0.1:5000/predict](http://127.0.0.1:5000/predict)'

def send_legacy_test(name, data):
    print(f"\n--- LEGACY TEST: {name} ---")
    resp = requests.post(url, json=data)
    if resp.status_code == 200:
        price = resp.json()['predicted_price']
        print(f"⚠️ DANGER: Model accepted bad data.")
        print(f"   Predicted Price: ${price:,.2f}")
    else:
        print("✅ Safe: Model crashed or blocked request (Unexpected for v3.0)")

# TEST A: The Mega Mansion (v3.0 will predict a low price for this)
send_legacy_test("Mega Mansion (200k SqFt)", {
    "GrLivArea": 200000,
    "OverallQual": 10,
    "Neighborhood": "NoRidge"
})
```
























