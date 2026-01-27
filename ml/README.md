# ML Model Training

This directory contains the machine learning model training code and trained models.

## Files

- `model_placeholder.py`: Placeholder script for training the price prediction model
- `trained_model.pkl`: Trained model file (created after training)

## Training a Model

To train a new model:

1. Ensure you have training data in the `data/` directory
2. Implement the training logic in `model_placeholder.py`
3. Run the training script:
   ```bash
   python ml/model_placeholder.py
   ```

## Model Details

The model should predict mobile phone prices based on the following features:

- Battery power (mAh)
- Bluetooth support
- Clock speed (GHz)
- Dual SIM support
- Front camera (MP)
- 4G support
- Internal memory (GB)
- Mobile depth (cm)
- Mobile weight (grams)
- Number of cores
- Primary camera (MP)
- Pixel resolution (height and width)
- RAM (MB)
- Screen size (height and width in cm)
- Talk time (hours)
- 3G support
- Touch screen support
- WiFi support

## Recommended Algorithms

Consider using one of these algorithms:
- Random Forest Regressor
- XGBoost
- Gradient Boosting
- Neural Networks

## Evaluation Metrics

Evaluate your model using:
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score
