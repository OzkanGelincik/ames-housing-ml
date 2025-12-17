import requests

url = 'http://127.0.0.1:5000/predict'

def send_test(name, data):
    print(f"\n--- TEST: {name} ---")
    print(f"Input: {data}")
    resp = requests.post(url, json=data)
    if resp.status_code == 200:
        price = resp.json()['predicted_price']
        print(f"💰 Price: ${price:,.2f}")
        return price
    else:
        print("❌ Failed")
        return 0

# TEST A: The Mega Mansion (Should be clamped to ~10k sq ft price)
# If this returns $100 Million, your guardrails failed.
# It should return something around $400k - $600k.
mansion_price = send_test("Mega Mansion (200k SqFt)", {
    "GrLivArea": 200000, 
    "OverallQual": 10,
    "Neighborhood": "NoRidge"
})

# TEST B: The Minimalist (Only providing 1 feature)
# The API must impute the other ~78 columns without crashing.
min_price = send_test("Minimalist (Only LotArea provided)", {
    "LotArea": 5000
})

# TEST C: The Unknown Category
# "MarsBase" is not a valid neighborhood. 
# The Pipeline should convert this to 'None' -> Unknown Integer -> Prediction.
mars_price = send_test("Unknown Category", {
    "Neighborhood": "MarsBase",
    "GrLivArea": 1000
})
