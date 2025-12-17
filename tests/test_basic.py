import requests
import json

# URL of your running Flask App
url = 'http://127.0.0.1:5000/predict'

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
    result = response.json()

    # CHECK 1: Did the server return a 200 OK?
    # CHECK 2: Did the JSON actually say "success"?
    if response.status_code == 200 and result.get('status') == 'success':
        print("\n✅ SUCCESS!")
        print(f"Predicted Price: ${result['predicted_price']:,.2f}")
        print(f"Server Version:  {result['version']}")
    else:
        # If it failed, print the error message sent by the server
        print(f"\n❌ SERVER ERROR: {result.get('message', 'Unknown Error')}")

except Exception as e:
    print(f"\n❌ Connection Refused. Is app_3.0.py running? \nError: {e}")
