"""Local credentials used by authentication flow."""

ADMIN_ROLE = "admin"
DATA_SCIENTIST_ROLE = "data_scientist"
USER_ROLE = "user"

ADMIN_PERMISSION_OPTIONS = [
    "user_management",
    "predict",
]

USER_PERMISSION_OPTIONS = ["predict"]

DATA_SCIENTIST_PERMISSION_OPTIONS = [
    "dashboard",
    "data_visualization",
    "model_management",
    "predict",
]

ADMIN_CREDENTIALS = {
    "admin1": "admin123",
    "admin2": "admin456",
    "admin3": "admin789",
}

DATA_SCIENTIST_CREDENTIALS = {
    "ds1": "ds123456",
}

USER_CREDENTIALS = {
    "student1": "stud123",
    "engineer1": "eng123",
    "recruiter1": "rec123",
}
