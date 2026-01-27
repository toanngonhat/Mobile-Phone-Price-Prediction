# ML Model Directory

This directory contains machine learning models and training scripts.

## Structure
- `model_placeholder.py` - Training pipeline template (to be implemented)
- `trained_model.pkl` - Trained model file (will be created after training)

## Future Implementation

### Model Training Steps:
1. Load dataset from `data/sample_phone_data.csv`
2. Preprocess features (encoding categorical variables, scaling)
3. Split data into training and validation sets
4. Train regression model (e.g., Random Forest, Gradient Boosting)
5. Evaluate model performance
6. Save trained model using pickle or joblib

### Model Requirements:
- Must be scikit-learn compatible (implement `.predict()` method)
- Accept input as numpy array or pandas DataFrame
- Return numeric predictions for phone prices

### Example Model Training:
```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import pickle

# Load and preprocess data
df = pd.read_csv('../data/sample_phone_data.csv')

# Feature engineering
# ... (encode brands, scale features)

# Train model
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

# Save model
with open('trained_model.pkl', 'wb') as f:
    pickle.dump(model, f)
```

## Integration
Once trained, the model will be loaded by `app/services/model_loader.py` and used by `app/services/prediction_service.py` for predictions.
