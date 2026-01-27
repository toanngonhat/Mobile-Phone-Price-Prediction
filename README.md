# Mobile Phone Price Prediction

A FastAPI-based RESTful API for predicting mobile phone prices based on device specifications and features.

## Project Structure

```
Mobile-Phone-Price-Prediction/
├── app/
│   ├── main.py                    # Main FastAPI application entry point
│   ├── routes/
│   │   ├── admin.py              # Admin routes (stats, model management, user management)
│   │   ├── user.py               # User routes (price prediction, feature info)
│   ├── services/
│   │   ├── prediction_service.py # Price prediction business logic
│   │   ├── model_loader.py       # ML model loading and management
│   ├── models/
│   │   ├── phone_features.py     # Pydantic models for request/response validation
│   ├── auth/
│   │   ├── roles.py              # Role-based access control (RBAC)
│   ├── utils/
│       ├── data_utils.py         # Data preprocessing and feature engineering utilities
├── data/
│   ├── sample_phone_data.csv     # Sample training data
├── ml/
│   ├── model_placeholder.py      # Model training script placeholder
│   ├── README.md                 # ML model documentation
├── requirements.txt               # Python dependencies
├── README.md                      # This file
```

## Features

- **RESTful API** for mobile phone price prediction
- **Role-based access control** with admin and user roles
- **Feature validation** using Pydantic models
- **Modular architecture** with clear separation of concerns
- **ML model management** with model loading and reloading capabilities
- **Comprehensive documentation** with OpenAPI/Swagger UI

## Installation

1. Clone the repository:
```bash
git clone https://github.com/toanngonhat/Mobile-Phone-Price-Prediction.git
cd Mobile-Phone-Price-Prediction
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the API Server

```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### API Endpoints

#### Public Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

#### User Endpoints (No authentication required for basic access)

- `POST /api/predict` - Predict mobile phone price based on features
- `GET /api/features` - Get information about required features

#### Admin Endpoints (Require admin API key)

- `GET /admin/stats` - Get application statistics
- `POST /admin/reload-model` - Reload the prediction model
- `GET /admin/users` - List all users

### Example: Making a Prediction

```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "battery_power": 1500,
    "blue": 1,
    "clock_speed": 2.5,
    "dual_sim": 1,
    "fc": 5,
    "four_g": 1,
    "int_memory": 64,
    "m_dep": 0.5,
    "mobile_wt": 150,
    "n_cores": 4,
    "pc": 12,
    "px_height": 1920,
    "px_width": 1080,
    "ram": 3000,
    "sc_h": 15,
    "sc_w": 8,
    "talk_time": 10,
    "three_g": 1,
    "touch_screen": 1,
    "wifi": 1
  }'
```

### Example: Admin Access

To access admin endpoints, include the API key in the request header:

```bash
curl -X GET "http://localhost:8000/admin/stats" \
  -H "x-api-key: admin-key-123"
```

## Phone Features

The prediction model uses the following features:

| Feature | Description | Range |
|---------|-------------|-------|
| battery_power | Battery capacity in mAh | 500-2000 |
| blue | Has Bluetooth | 0 or 1 |
| clock_speed | Processor clock speed in GHz | 0.5-3.0 |
| dual_sim | Supports dual SIM | 0 or 1 |
| fc | Front camera megapixels | 0-20 |
| four_g | Has 4G support | 0 or 1 |
| int_memory | Internal memory in GB | 2-256 |
| m_dep | Mobile depth in cm | 0.1-1.0 |
| mobile_wt | Weight in grams | 80-200 |
| n_cores | Number of processor cores | 1-8 |
| pc | Primary camera megapixels | 0-20 |
| px_height | Pixel resolution height | 0-1960 |
| px_width | Pixel resolution width | 500-1998 |
| ram | RAM in MB | 256-4000 |
| sc_h | Screen height in cm | 5-19 |
| sc_w | Screen width in cm | 0-18 |
| talk_time | Battery talk time in hours | 2-20 |
| three_g | Has 3G support | 0 or 1 |
| touch_screen | Has touch screen | 0 or 1 |
| wifi | Has WiFi | 0 or 1 |

## Training a Custom Model

To train your own prediction model:

1. Prepare your training data in CSV format (see `data/sample_phone_data.csv` for example)
2. Implement the training logic in `ml/model_placeholder.py`
3. Run the training script:
```bash
python ml/model_placeholder.py
```

4. The trained model will be saved to `ml/trained_model.pkl`

See `ml/README.md` for more details on model training.

## Architecture

### Application Layer (`app/`)
- **main.py**: FastAPI application initialization and configuration
- **routes/**: API endpoint definitions
  - `admin.py`: Administrative operations
  - `user.py`: User-facing prediction endpoints
- **services/**: Business logic layer
  - `prediction_service.py`: Price prediction logic
  - `model_loader.py`: ML model management
- **models/**: Data models and schemas
  - `phone_features.py`: Pydantic models for validation
- **auth/**: Authentication and authorization
  - `roles.py`: Role-based access control
- **utils/**: Utility functions
  - `data_utils.py`: Data preprocessing and feature engineering

### Data Layer (`data/`)
Contains training and sample data files

### ML Layer (`ml/`)
Contains model training scripts and trained models

## Development

### Code Style

The project follows Python best practices:
- Clear separation of concerns
- Dependency injection
- Type hints using Pydantic
- Comprehensive docstrings

### Adding New Features

1. Define data models in `app/models/`
2. Implement business logic in `app/services/`
3. Create API endpoints in `app/routes/`
4. Update utilities in `app/utils/` as needed

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.