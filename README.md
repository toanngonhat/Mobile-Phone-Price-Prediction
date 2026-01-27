# Mobile Phone Price Prediction API

Backend API for predicting mobile phone prices based on specifications using machine learning.

## Features

### Admin Role
- Upload training datasets (CSV format)
- Upload/replace ML models
- View dataset statistics

### User Role
- Input mobile phone specifications
- Get predicted price

## Tech Stack
- **Framework**: FastAPI
- **ML**: scikit-learn (placeholder for future integration)
- **Data**: pandas, numpy
- **Python**: 3.9+

## Authentication

### Admin Credentials
- Username: `admin1`, Password: `admin123`
- Username: `admin2`, Password: `admin456`
- Username: `admin3`, Password: `admin789`

### User Credentials
- Username: `student1`, Password: `stud123`
- Username: `engineer1`, Password: `eng123`
- Username: `recruiter1`, Password: `rec123`

## Project Structure

```
mobile-phone-price-predictor/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app entry point
│   ├── routes/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── admin.py             # Admin endpoints
│   │   └── user.py              # User endpoints
│   ├── services/                 # Business logic layer
│   │   ├── __init__.py
│   │   ├── prediction_service.py # Price prediction logic
│   │   └── model_loader.py       # ML model management
│   ├── models/                   # Pydantic schemas
│   │   ├── __init__.py
│   │   └── phone_features.py     # Phone specs models
│   ├── auth/                     # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── roles.py              # Role-based access control
│   │   └── credentials.py        # User credentials
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       └── data_utils.py         # Dataset handling
├── data/                         # Dataset storage
│   └── sample_phone_data.csv
├── ml/                           # ML models and training scripts
│   ├── model_placeholder.py
│   └── README.md
└── requirements.txt              # Python dependencies
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

```bash
# Start the server
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

Interactive API docs: `http://localhost:8000/docs`

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/login` - Login with username and password
- `GET /api/auth/check` - Check authentication service status

### Admin Endpoints
- `POST /api/admin/upload-dataset` - Upload training dataset
- `POST /api/admin/upload-model` - Upload trained model
- `GET /api/admin/dataset-stats` - View dataset statistics

### User Endpoints
- `POST /api/user/predict-price` - Predict phone price
- `GET /api/user/health` - Health check

## Phone Features

The prediction model accepts the following phone specifications:
- **brand**: Phone manufacturer (Apple, Samsung, Google, Xiaomi, OnePlus, etc.)
- **ram**: RAM in GB (1-32)
- **storage**: Storage in GB (8-1024)
- **battery_capacity**: Battery capacity in mAh (1000-10000)
- **screen_size**: Screen size in inches (3.0-10.0)
- **camera_mp**: Main camera megapixels (2-200)

## Future Enhancements

- [ ] Train actual ML model with real dataset
- [ ] Implement JWT-based authentication tokens
- [ ] Add database integration (PostgreSQL/MongoDB)
- [ ] Add model versioning and A/B testing
- [ ] Add comprehensive logging and monitoring
- [ ] Add unit and integration tests
- [ ] Add Docker containerization
- [ ] Add CI/CD pipeline
- [ ] Add password hashing with bcrypt

## Development Notes

### Authentication
The current implementation uses simple token-based authentication with hardcoded credentials. For production:
- Implement JWT tokens with expiration
- Hash passwords using bcrypt or argon2
- Store credentials in a secure database
- Add token refresh mechanism

### Mock Prediction
Currently, the API uses a mock prediction algorithm based on simple heuristics. This should be replaced with a trained ML model.

### Model Integration
To integrate a real ML model:
1. Train your model using `ml/model_placeholder.py` as a template
2. Save the model as `ml/trained_model.pkl`
3. The `model_loader.py` will automatically load it
4. Update `prediction_service.py` to use actual model predictions


License
Copyright (c) 2025 University of Technology - Ho Chi Minh City Vietnam National University

Intelligence System Course

## Contributors

- **Ngo Nhat Toan**
  - Email: toan.ngonhat@hcmut.edu.vn

---
For questions, issues, or contributions, please open an issue on GitHub or contact the developers via email.
