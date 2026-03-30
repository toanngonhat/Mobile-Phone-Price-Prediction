# Mobile Phone Price Prediction

Mobile phone price prediction system using Random Forest on localhost web UI.

## Features

### Admin Role
- Train Random Forest model from Kaggle + synthetic iPhone data
- View dataset statistics and visualization charts
- Manage users, permissions, and model versions
- Predict phone price with model_branch templates

### Data Scientist Role
- Same analytics and model-management capabilities as Admin
- No access to User Management
- Can train models, view visualizations, switch model versions, and predict prices

### User Role
- Input mobile phone specifications
- Predict phone price

UI behavior:
- Input supports `model` + `branch` and maps to BE hash map `model_branch`.
- If `branch = iPhone`, RAM is auto-handled in backend (no manual RAM selection).
- `battery` unknown defaults to 80 (health %), then converted to effective battery capacity.

## Tech Stack
- **ML**: scikit-learn Random Forest
- **Data**: pandas, numpy, kagglehub
- **Python**: 3.9+

## Authentication

### Admin Credentials
- Username: `admin1`, Password: `admin123`
- Username: `admin2`, Password: `admin456`
- Username: `admin3`, Password: `admin789`

### Data Scientist Credentials
- Username: `ds1`, Password: `ds123456`

### User Credentials
- Username: `student1`, Password: `stud123`
- Username: `engineer1`, Password: `eng123`
- Username: `recruiter1`, Password: `rec123`

## Installation

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Application

### Localhost Web UI

```bash
python app.py
```

Open: http://127.0.0.1:8000

### Direct Training Command

```bash
python train.py --records 1000 --distribution latest_heavy
```

Supported distributions:
- `uniform`
- `latest_heavy`
- `promax_heavy`

## Phone Features for Prediction

- **brand**: manufacturer name
- **ram**: 1-32 GB
- **storage**: 8-1024 GB
- **battery_capacity**: 1000-10000 mAh
- **screen_size**: 3.0-10.0 inches
- **camera_mp**: 2-200 MP

## Model Notes

1. Source dataset: `ahsan81/used-handheld-device-data`
2. Synthetic iPhone 11-15 data is merged for training
3. Columns `4g` and `5g` are excluded
4. Versioned models are stored in `app/model_versions`

License
Copyright (c) 2025 University of Technology - Ho Chi Minh City Vietnam National University
