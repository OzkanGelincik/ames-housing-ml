import requests

# The URL where your local server is living
url = 'http://127.0.0.1:5000/predict'

# 1. A Normal House
house_data = {
    "GrLivArea": 2500,
    "OverallQual": 8,
    "YearBuilt": 2010,
    "GarageCars": 3,
    "TotalBsmtSF": 1000
}

# 2. A "Mega Mansion" Attack (200,000 sq ft)
attack_data = {
    "GrLivArea": 200000, 
    "OverallQual": 10,
    "YearBuilt": 2024
}

print("--- Sending Normal Request ---")
response = requests.post(url, json=house_data)
print(response.json())

print("\n--- Sending 'Attack' Request ---")
response = requests.post(url, json=attack_data)
print(response.json())
