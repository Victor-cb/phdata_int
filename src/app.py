import json
import pickle
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration: Support both local and versioned deployments
MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0')
MODEL_DIR = os.getenv('MODEL_DIR', 'model')  # Can point to different directories

# Paths
DEMOGRAPHICS_PATH = Path("data/zipcode_demographics.csv")

# Global state
model = None
required_features = None
demographics_df = None
model_loaded_at = None


def load_model_artifacts():
    global model, required_features, demographics_df, model_loaded_at
    
    model_path = Path(MODEL_DIR) / "model.pkl"
    features_path = Path(MODEL_DIR) / "model_features.json"
    
    print(f"Loading model version {MODEL_VERSION} from {MODEL_DIR}...")
    
    # Load model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # Load features
    with open(features_path, 'r') as f:
        required_features = json.load(f)
    
    # Load demographics (shared across versions)
    demographics_df = pd.read_csv(DEMOGRAPHICS_PATH, dtype={'zipcode': str})
    
    model_loaded_at = datetime.now()
    

# Load model at startup
load_model_artifacts()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "model_version": MODEL_VERSION,
        "model_loaded_at": model_loaded_at.isoformat() if model_loaded_at else None
    })


@app.route('/model/info', methods=['GET'])
def model_info():
    return jsonify({
        "model_version": MODEL_VERSION,
        "model_directory": MODEL_DIR,
        "features_count": len(required_features) if required_features else 0,
        "features": required_features,
        "loaded_at": model_loaded_at.isoformat() if model_loaded_at else None,
        "demographics_zipcodes": len(demographics_df) if demographics_df is not None else 0
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Full prediction endpoint - accepts all house features."""
    try:
        data = request.get_json()
        
        if 'zipcode' in data:
            data['zipcode'] = str(int(float(data['zipcode']))) #prevent user input
        
        input_df = pd.DataFrame([data])
        
        if 'zipcode' in input_df.columns:
            input_df['zipcode'] = input_df['zipcode'].astype(str)
        
        merged_df = input_df.merge(demographics_df, how='left', on='zipcode') #add demographics
        merged_df = merged_df.drop(columns=['zipcode'])
        
        feature_df = merged_df[required_features] #model features only
        
        if feature_df.isnull().any().any():
            missing_cols = feature_df.columns[feature_df.isnull().any()].tolist()
            return jsonify({"error": f"Missing features to predictions, columns missing {missing_cols}"}), 400
        
        prediction = model.predict(feature_df)[0] # predictions
        
        return jsonify({
            "prediction": float(prediction),
            "model_version": MODEL_VERSION,
            "features_used": required_features,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/predict/minimal', methods=['POST'])
def predict_minimal(): # Bonus
    try:
        data = request.get_json()
        
        minimal_features = ['bedrooms', 'bathrooms', 'sqft_living', 'sqft_lot', 
                           'floors', 'sqft_above', 'sqft_basement', 'zipcode']
        
        missing = [f for f in minimal_features if f not in data]
        if missing:
            return jsonify({"error": f"Missing required fields: {missing}"}), 400
        
        data['zipcode'] = str(int(float(data['zipcode'])))
        
        input_df = pd.DataFrame([{k: data[k] for k in minimal_features}])
        input_df['zipcode'] = input_df['zipcode'].astype(str)
        merged_df = input_df.merge(demographics_df, how='left', on='zipcode')
        merged_df = merged_df.drop(columns=['zipcode'])
        
        if merged_df.isnull().any().any():
            missing_cols = merged_df.columns[merged_df.isnull().any()].tolist()
            return jsonify({"error": f"Missing features to predictions, columns missing {missing_cols}"}), 400
        
        feature_df = merged_df[required_features]
        prediction = model.predict(feature_df)[0]
        
        return jsonify({
            "prediction": float(prediction),
            "model_version": MODEL_VERSION,
            "minimal_features_used": minimal_features,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
