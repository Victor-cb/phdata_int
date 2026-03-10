import json
import requests
import pandas as pd

# BASE_URL = "http://localhost"
import argparse
import sys

parser = argparse.ArgumentParser(description='Test ML API deployment type')
parser.add_argument('--mode', choices=['direct', 'bluegreen'], default='direct',
                    help='Deployment mode: direct (port 8080) or bluegreen (nginx port 80)')
args = parser.parse_args()

if args.mode == 'bluegreen':
    BASE_URL = "http://localhost"  # nginx on port 80
    DEPLOYMENT_NAME = "Blue-Green Deployment (nginx)"
    print(f"\n Testing BLUE-GREEN deployment (nginx on port 80)\n")
else:
    BASE_URL = "http://localhost:8080"  # direct docker
    DEPLOYMENT_NAME = "Direct Deployment"
    print(f"\n Testing DIRECT deployment (docker on port 8080)\n")

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:")
    print(json.dumps(response.json(), indent=2))

def test_full_prediction():
    print("Testing Full Prediction Endpoint:")
    examples = pd.read_csv("data/future_unseen_examples.csv")
    
    example = examples.iloc[0].to_dict()    
    print(f"Features input: {json.dumps(example, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/predict", json=example)
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_minimal_prediction():
    print("Testing Minimal Prediction Endpoint:")

    examples = pd.read_csv("data/future_unseen_examples.csv")
    
    minimal_features = ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                       'floors', 'sqft_above', 'sqft_basement', 'zipcode']
    
    example = examples.iloc[0][minimal_features].to_dict()
    
    print(f"Features Input: {json.dumps(example, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/predict/minimal", json=example)
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_multiple_predictions():
    examples = pd.read_csv("data/future_unseen_examples.csv")
    
    print("Testing first 5 examples:")
    predictions = []
    
    for idx in range(min(5, len(examples))):
        example = examples.iloc[idx].to_dict()
        response = requests.post(f"{BASE_URL}/predict", json=example)
        
        if response.status_code == 200:
            pred = response.json()['prediction']
            predictions.append(pred)
            print(f"Example {idx + 1}: ${pred:,.2f}")
        else:
            print(f"Example {idx + 1}: Error - {response.json()}")
    
    print(f"\nAverage prediction: ${sum(predictions)/len(predictions):,.2f}")

if __name__ == "__main__":
    print("Sound Realty Model API Test Suite")
    
    try:
        test_health()
        test_full_prediction()
        test_minimal_prediction()
        test_multiple_predictions()
        
        print("Tests ok!")
    
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API.")
        print("Start the server with: docker-compose up")
    except Exception as e:
        print(f"Error during testing: {e}")
