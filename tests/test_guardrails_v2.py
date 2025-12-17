import requests

BASE_URL = "http://127.0.0.1:5000/predict"

def test_request(name, data):
    print(f"\n--- TEST: {name} ---")
    print(f"Input: {data}")
    
    try:
        response = requests.post(BASE_URL, json=data)
        
        # SCENARIO 1: Success (200 OK) - We expected a price
        if response.status_code == 200:
            result = response.json()
            print(f"💰 Price: ${result['predicted_price']:,.2f}")
            print(f"ℹ️  Version: {result.get('version', 'N/A')}")
            
        # SCENARIO 2: Guardrail Blocked It (400 Bad Request) - THIS IS GOOD FOR BAD DATA
        elif response.status_code == 400:
            error_data = response.json()
            print("✅ GUARDRAIL ACTIVE: Request Blocked.")
            print(f"   Reason: {error_data['details'][0]['msg']}")
            print(f"   Field:  {error_data['details'][0]['loc']}")

        # SCENARIO 3: Server Crash (500)
        else:
            print(f"❌ SERVER ERROR ({response.status_code}): {response.text}")
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

# ==========================================
# RUN TESTS
# ==========================================

# 1. Mega Mansion (Should Fail: Too Big)
test_request(
    "Mega Mansion (200k SqFt)", 
    {'GrLivArea': 200000, 'OverallQual': 10, 'Neighborhood': 'NoRidge', 'YearBuilt': 2000}
)

# 2. Minimalist (Should Fail: Missing Required Fields)
test_request(
    "Minimalist (Missing Data)", 
    {'LotArea': 5000}
)

# 3. Valid House (Should Succeed)
test_request(
    "Standard House (Control Test)", 
    {'Neighborhood': 'CollgCr', 'GrLivArea': 1500, 'YearBuilt': 2005, 'OverallQual': 7}
)