import json
import pickle
from pathlib import Path
from datetime import datetime
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

MODEL_PATH = Path("model/model.pkl")
FEATURES_PATH = Path("model/model_features.json")
DEMOGRAPHICS_PATH = Path("data/zipcode_demographics.csv")

model = None
required_features = None
demographics_df = None


def load_model_features():

    global model, required_features, demographics_df
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    
    with open(FEATURES_PATH, 'r') as f:
        required_features = json.load(f)
    
    demographics_df = pd.read_csv(DEMOGRAPHICS_PATH, dtype={'zipcode': str})

load_model_features()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "model_loaded": model is not None})


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
            "model_version": "1.0",
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
            "model_version": "1.0",
            "minimal_features_used": minimal_features,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
