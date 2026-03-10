#Example request in the API
import requests
import json

API_URL = "http://localhost"

def example_full_prediction():
    print("Example 1: Full Prediction")

    # House data
    house_data = {
        "bedrooms": 3,
        "bathrooms": 2.5,
        "sqft_living": 2220,
        "sqft_lot": 6380,
        "floors": 1.5,
        "waterfront": 0,
        "view": 0,
        "condition": 4,
        "grade": 8,
        "sqft_above": 1660,
        "sqft_basement": 560,
        "yr_built": 1931,
        "yr_renovated": 0,
        "zipcode": "98115",
        "lat": 47.6974,
        "long": -122.313,
        "sqft_living15": 950,
        "sqft_lot15": 6380
    }
    
    response = requests.post(f"{API_URL}/predict", json=house_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n- Predicted Price: ${result['prediction']:,.2f}\n- Model version: {result['model_version']}")
    else:
        print(f"\n✗ Error: {response.json()}")
    
    print()


def example_minimal_prediction():
    print("Example 2: (Bonus Endpoint)")
    
    # Only required features
    house_data = { 
        "bedrooms": 5,
        "bathrooms": 2.5,
        "sqft_living": 1710,
        "sqft_lot": 9720,
        "floors": 2.0,
        "sqft_above": 1710,
        "sqft_basement": 0,
        "zipcode": "98005"
    }
    
    
    response = requests.post(f"{API_URL}/predict/minimal", json=house_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"""  \n- Predicted Price: ${result['prediction']:,.2f}
                    \n- Model version: {result['model_version']}
                    \n- Features Used: {len(result['minimal_features_used'])}
                """)
    else:
        print(f"\n✗ Error: {response.json()}")
    
    print()


def example_error_handling():
    print("Example 3: Error Handling")
    
    # Missing required field
    incomplete_data = {
        "bedrooms": 3,
        "bathrooms": 2.0,
    }
    
    print("\nInput: Incomplete data (missing required fields)")
    
    response = requests.post(f"{API_URL}/predict/minimal", json=incomplete_data)
    
    if response.status_code == 400:
        print(f"\n API correctly rejected invalid input:")
        print(f"  {response.json()['error']}")
    else:
        print(f"\n✗ Unexpected response: {response.json()}")
    
    print()


if __name__ == "__main__":
    print("  \n\nSound Realty House Price Prediction API           ")
    print("           Example Usage\n\n                             ")
    
    try:
        # Check if API is running
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            print("Heatlh check - Pass. \nRunning Predictions\n")
        
        # Run examples
        example_full_prediction()
        example_minimal_prediction()
        example_error_handling()
        
        print("Examples completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API")
        print("\nPlease start the API first:")
        print("  Docker:  docker-compose up")
        print("  Local:   ./start_local.sh")
        print()
