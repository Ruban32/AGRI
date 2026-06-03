"""
ML Model Training Script
Trains crop recommendation, fertilizer recommendation, and yield prediction models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

print("=" * 60)
print("AI-Powered Smart Agriculture System - Model Training")
print("=" * 60)

# ==================== CROP RECOMMENDATION MODEL ====================
print("\n[1/3] Training Crop Recommendation Model...")

# Create synthetic dataset for crop recommendation
np.random.seed(42)
n_samples = 2200

crop_data = pd.DataFrame({
    'nitrogen': np.random.randint(20, 140, n_samples),
    'phosphorus': np.random.randint(5, 145, n_samples),
    'potassium': np.random.randint(9, 205, n_samples),
    'ph': np.random.uniform(5.0, 8.5, n_samples),
    'rainfall': np.random.randint(200, 2500, n_samples),
    'temperature': np.random.uniform(10, 45, n_samples),
    'humidity': np.random.randint(30, 100, n_samples)
})

# Generate crop labels based on conditions
crop_labels = []
for idx, row in crop_data.iterrows():
    if row['nitrogen'] > 100 and row['rainfall'] > 1500:
        crop = 'Rice'
    elif row['nitrogen'] > 90 and row['temperature'] < 25 and row['rainfall'] < 1500:
        crop = 'Wheat'
    elif row['nitrogen'] > 110 and row['temperature'] > 25:
        crop = 'Maize'
    elif row['potassium'] > 180 and row['temperature'] > 28:
        crop = 'Cotton'
    elif row['rainfall'] > 2000 and row['nitrogen'] > 100:
        crop = 'Sugarcane'
    elif row['temperature'] < 25 and row['potassium'] > 150:
        crop = 'Potato'
    elif row['temperature'] > 25 and row['humidity'] > 60:
        crop = 'Tomato'
    else:
        crop = 'Onion'
    crop_labels.append(crop)

crop_data['crop'] = crop_labels

# Train crop recommendation model
X_crop = crop_data[['nitrogen', 'phosphorus', 'potassium', 'ph', 'rainfall', 'temperature', 'humidity']]
y_crop = crop_data['crop']

X_train_crop, X_test_crop, y_train_crop, y_test_crop = train_test_split(
    X_crop, y_crop, test_size=0.2, random_state=42
)

crop_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
crop_model.fit(X_train_crop, y_train_crop)

crop_accuracy = crop_model.score(X_test_crop, y_test_crop)
print(f"   ✓ Crop Recommendation Model trained")
print(f"   ✓ Accuracy: {crop_accuracy:.2%}")
print(f"   ✓ Crops: {', '.join(crop_data['crop'].unique())}")

# Save crop model
joblib.dump(crop_model, 'models/crop_recommendation_model.pkl')
print(f"   ✓ Model saved to: models/crop_recommendation_model.pkl")


# ==================== FERTILIZER RECOMMENDATION MODEL ====================
print("\n[2/3] Training Fertilizer Recommendation Model...")

# Create synthetic dataset for fertilizer recommendation
fertilizer_data = pd.DataFrame({
    'nitrogen': np.random.randint(20, 140, n_samples),
    'phosphorus': np.random.randint(5, 145, n_samples),
    'potassium': np.random.randint(9, 205, n_samples),
    'crop': np.random.choice(['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Potato', 'Tomato', 'Onion'], n_samples),
    'soil_type': np.random.choice(['Loamy', 'Clay', 'Sandy', 'Silt', 'Peat', 'Alluvial'], n_samples),
    'moisture': np.random.uniform(10, 50, n_samples)
})

# Generate fertilizer recommendations
fertilizer_labels = []
for idx, row in fertilizer_data.iterrows():
    if row['nitrogen'] < 40:
        fert = 'Urea'
    elif row['phosphorus'] < 30:
        fert = 'DAP (Di-ammonium phosphate)'
    elif row['potassium'] < 60:
        fert = 'MOP (Muriate of Potash)'
    elif row['crop'] in ['Potato', 'Tomato', 'Onion']:
        fert = 'Vermicompost'
    elif row['soil_type'] in ['Clay', 'Sandy']:
        fert = 'Compost'
    else:
        fert = 'NPK 10-10-10'
    fertilizer_labels.append(fert)

fertilizer_data['fertilizer'] = fertilizer_labels

# Encode categorical variables
le_crop = LabelEncoder()
le_soil = LabelEncoder()
fertilizer_data['crop_encoded'] = le_crop.fit_transform(fertilizer_data['crop'])
fertilizer_data['soil_encoded'] = le_soil.fit_transform(fertilizer_data['soil_type'])

# Train fertilizer recommendation model
X_fert = fertilizer_data[['nitrogen', 'phosphorus', 'potassium', 'crop_encoded', 'soil_encoded', 'moisture']]
y_fert = fertilizer_data['fertilizer']

X_train_fert, X_test_fert, y_train_fert, y_test_fert = train_test_split(
    X_fert, y_fert, test_size=0.2, random_state=42
)

fertilizer_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
fertilizer_model.fit(X_train_fert, y_train_fert)

fert_accuracy = fertilizer_model.score(X_test_fert, y_test_fert)
print(f"   ✓ Fertilizer Recommendation Model trained")
print(f"   ✓ Accuracy: {fert_accuracy:.2%}")
print(f"   ✓ Fertilizers: {', '.join(fertilizer_data['fertilizer'].unique())}")

# Save fertilizer model
joblib.dump(fertilizer_model, 'models/fertilizer_recommendation_model.pkl')
print(f"   ✓ Model saved to: models/fertilizer_recommendation_model.pkl")


# ==================== YIELD PREDICTION MODEL ====================
print("\n[3/3] Training Yield Prediction Model...")

# Create synthetic dataset for yield prediction
yield_data = pd.DataFrame({
    'crop': np.random.choice(['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Potato', 'Tomato', 'Onion'], n_samples),
    'area': np.random.uniform(1, 100, n_samples),
    'rainfall': np.random.randint(200, 2500, n_samples),
    'temperature': np.random.uniform(10, 45, n_samples),
    'nitrogen': np.random.randint(20, 140, n_samples),
    'phosphorus': np.random.randint(5, 145, n_samples),
    'potassium': np.random.randint(9, 205, n_samples)
})

# Generate yield values (realistic estimates based on crop and inputs)
yields = []
for idx, row in yield_data.iterrows():
    base_yield = 40  # base yield in kg/hectare
    
    # Adjust based on crop type
    if row['crop'] == 'Rice':
        base_yield = 5000
    elif row['crop'] == 'Wheat':
        base_yield = 4000
    elif row['crop'] == 'Maize':
        base_yield = 6000
    elif row['crop'] == 'Cotton':
        base_yield = 2000
    elif row['crop'] == 'Sugarcane':
        base_yield = 80000
    elif row['crop'] == 'Potato':
        base_yield = 20000
    elif row['crop'] == 'Tomato':
        base_yield = 50000
    else:  # Onion
        base_yield = 40000
    
    # Adjust based on conditions
    npk_factor = (row['nitrogen'] + row['phosphorus'] + row['potassium']) / 300
    rainfall_factor = max(0.5, min(1.5, row['rainfall'] / 1500))
    temp_factor = max(0.7, min(1.3, (25 - abs(row['temperature'] - 25)) / 20))
    area_efficiency = max(0.8, min(1.2, row['area'] / 20))
    
    final_yield = base_yield * npk_factor * rainfall_factor * temp_factor * area_efficiency
    final_yield = max(100, final_yield)  # Ensure minimum yield
    yields.append(final_yield + np.random.normal(0, final_yield * 0.1))

yield_data['yield'] = yields

# Encode crop variable
le_crop_yield = LabelEncoder()
yield_data['crop_encoded'] = le_crop_yield.fit_transform(yield_data['crop'])

# Train yield prediction model (regression)
X_yield = yield_data[['crop_encoded', 'area', 'rainfall', 'temperature', 'nitrogen', 'phosphorus', 'potassium']]
y_yield = yield_data['yield']

X_train_yield, X_test_yield, y_train_yield, y_test_yield = train_test_split(
    X_yield, y_yield, test_size=0.2, random_state=42
)

yield_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
yield_model.fit(X_train_yield, y_train_yield)

yield_r2 = yield_model.score(X_test_yield, y_test_yield)
print(f"   ✓ Yield Prediction Model trained")
print(f"   ✓ R² Score: {yield_r2:.2%}")

# Save yield model
joblib.dump(yield_model, 'models/yield_prediction_model.pkl')
print(f"   ✓ Model saved to: models/yield_prediction_model.pkl")


# ==================== SAVE ENCODERS ====================
print("\n[4/4] Saving Encoders...")

joblib.dump(le_crop, 'models/crop_encoder.pkl')
joblib.dump(le_crop_yield, 'models/crop_encoder_yield.pkl')
joblib.dump(le_soil, 'models/soil_encoder.pkl')

print("   ✓ Encoders saved successfully")

# ==================== SUMMARY ====================
print("\n" + "=" * 60)
print("MODEL TRAINING SUMMARY")
print("=" * 60)
print(f"✓ Crop Recommendation Model Accuracy: {crop_accuracy:.2%}")
print(f"✓ Fertilizer Recommendation Model Accuracy: {fert_accuracy:.2%}")
print(f"✓ Yield Prediction Model R² Score: {yield_r2:.2%}")
print("\nAll models trained and saved successfully!")
print("=" * 60)
