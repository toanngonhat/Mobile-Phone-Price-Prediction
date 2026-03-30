# Mobile Phone Price Prediction

A machine learning web application for predicting used mobile phone prices using Random Forest regression. The system includes role-based authentication, model version management, data visualization, dataset operations, and localhost deployment.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [User Roles and Workflows](#user-roles-and-workflows)
- [Model Features and Training](#model-features-and-training)
- [Model Manager: Add Records](#model-manager-add-records)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This project predicts resale prices of mobile phones from structured device specifications. It uses a Random Forest pipeline, supports model versioning, and provides role-specific dashboard experiences:

- Admin: full management (users, models, visualizations)
- Data Scientist: model and analytics management (no user management)
- User: prediction-only workflow

The app is designed to run locally on `127.0.0.1:8000`.

## Features

### User-Facing Features

- Role-based login for Admin, Data Scientist, and User
- Single mobile price prediction from form inputs
- Dashboard sections for model versions, charts, and stats
- Model training with configurable synthetic record generation
- Dataset summary rendered in table format
- Manual one-row record insertion from UI
- CSV batch record import for dataset append

### Technical Features

- Random Forest model with preprocessing pipeline
- Feature handling with categorical + numerical transformers
- Model versioning with metadata storage (`v1`, `v2`, `v3`, ...)
- Active model switching at runtime
- Dataset build flow from Kaggle + synthetic iPhone generation
- CSV ingestion with dual schema support:
  - normalized prices (`normalized_used_price`, `normalized_new_price`)
  - raw prices (`used_price`, `new_price`) with auto conversion to logs

## System Architecture

The application follows an MVC-style structure with Flask routing.

### Layers

1. Presentation Layer
- Flask templates for login and dashboard views
- Role-specific dashboard sections

2. Controller Layer
- Authentication workflows
- User prediction workflows
- Admin/Data Scientist management workflows

3. Model Layer
- `PhonePriceModel` for dataset build, training, loading, and inference
- Versioned model artifacts and metrics

4. Data and Config Layer
- Centralized project settings
- Device catalog mappings
- Local dataset and app settings persistence

### Data Flow

User Input -> Flask Route -> Controller Logic -> Model Inference/Training -> UI Rendering

## Installation and Setup

### Prerequisites

- Python 3.9+
- pip

### Setup Steps

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

Open: `http://127.0.0.1:8000`

### Direct Training Command

```bash
python train.py --records 1000 --distribution latest_heavy
```

Supported distributions:

- `uniform`
- `latest_heavy`
- `promax_heavy`

## User Roles and Workflows

### 1. Admin

Credentials:

- `admin1` / `admin123`
- `admin2` / `admin456`
- `admin3` / `admin789`

Capabilities:

- Dashboard home and system overview
- User Management:
  - view users
  - add/edit/delete users
  - manage permissions
- Data Visualization:
  - feature importance
  - model performance metrics
  - price distribution
  - days-used vs price correlation
- Model Management:
  - view model versions
  - switch active version
  - delete outdated versions
  - train new model
  - add manual dataset row
  - import dataset rows from CSV

### 2. Data Scientist

Credentials:

- `ds1` / `ds123456`

Capabilities:

- Same model and analytics capabilities as Admin
- No access to User Management

### 3. User

Credentials:

- `student1` / `stud123`
- `engineer1` / `eng123`
- `recruiter1` / `rec123`

Capabilities:

- Predict mobile price from device specifications

## Model Features and Training

### Prediction Features

The model predicts from these engineered runtime inputs:

- `brand`
- `ram`
- `storage`
- `battery_capacity`
- `screen_size`
- `camera_mp`

### Raw Dataset Schema

Training data schema:

- `device_brand`
- `os`
- `screen_size`
- `rear_camera_mp`
- `front_camera_mp`
- `internal_memory`
- `ram`
- `battery`
- `weight`
- `release_year`
- `days_used`
- `normalized_used_price`
- `normalized_new_price`

### Training Output

Each training run creates a new version directory with:

- `model.pkl`
- `metadata.json` (R2, MAE, RMSE, records, timestamp, features)

## Model Manager: Add Records

Model Manager supports two data append flows.

### 1. Manual Single Row

Input one row from UI fields and append to the dataset.

### 2. CSV Batch Import

Upload CSV using one of the following formats:

1. Full normalized schema
- Must include `normalized_used_price` and `normalized_new_price`

2. Raw price schema
- Use `used_price` and `new_price`
- System auto converts to log values for normalized columns

Validation rules:

- Required columns must exist
- `used_price` and `new_price` must be positive
- Numeric columns are type-cast before append

## Project Structure

```text
Mobile-Phone-Price-Prediction/
├── app.py
├── train.py
├── start.sh
├── requirements.txt
├── README.md
├── app/
│   ├── app.py
│   ├── app_settings.json
│   ├── config/
│   │   ├── credentials.py
│   │   ├── device_catalog.py
│   │   └── settings.py
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── admin_controller.py
│   │   └── user_controller.py
│   ├── data/
│   │   └── sample_phone_data.csv
│   ├── models/
│   │   └── phone_price_model.py
│   ├── model_versions/
│   │   ├── v1/
│   │   ├── v2/
│   │   └── v3/
│   ├── templates/
│   │   ├── login.html
│   │   └── dashboard.html
│   └── utils/
│       └── data_utils.py
```

## Configuration

Main settings are in `app/config/settings.py`.

Important values:

- Dataset path
- Model versions directory
- App settings path
- Kaggle dataset reference
- Feature columns and raw schema

Runtime app state is stored in `app/app_settings.json`.

Example:

```json
{
  "active_model_version": 3,
  "last_training_time": "2026-03-29T16:45:20.768482+00:00"
}
```

## Usage Examples

### Example 1: Predict a Mobile Price

1. Login as a user account
2. Choose brand and model
3. Enter device details
4. Submit prediction form
5. Read predicted price in dashboard

### Example 2: Train New Model

1. Login as Admin or Data Scientist
2. Open Model Management
3. Set records and distribution profile
4. Optionally enable append-only mode
5. Click Train Model and review metrics

### Example 3: Import CSV Records

1. Open Model Management
2. Use Import Multiple Records (CSV)
3. Upload valid CSV schema
4. System appends rows and shows success message

## Troubleshooting

### 1. Port Already in Use

If app fails to start on port 8000, stop old process or change run config.

### 2. CSV Upload Fails

Check:

- file extension is `.csv`
- required columns are present
- price columns are positive
- numeric fields are numeric

### 3. No Model Found for Prediction

Train at least one model version first from Model Management.

### 4. Access Denied to User Management

Expected behavior for `data_scientist` role. Use Admin role for user operations.

## License

Copyright (c) 2025 University of Technology - Ho Chi Minh City Vietnam National University
