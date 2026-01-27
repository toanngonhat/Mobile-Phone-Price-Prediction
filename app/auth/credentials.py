"""
User credentials and authentication data.
Stores valid usernames, passwords, and roles.
"""
from typing import Optional

# Admin credentials
ADMIN_CREDENTIALS = {
    "admin1": "admin123",
    "admin2": "admin456",
    "admin3": "admin789",
}

# User credentials
USER_CREDENTIALS = {
    "student1": "stud123",
    "engineer1": "eng123",
    "recruiter1": "rec123",
}


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify if username and password combination is valid.

    Args:
        username: Username to check
        password: Password to verify

    Returns:
        True if credentials are valid, False otherwise
    """
    # Check admin credentials
    if username in ADMIN_CREDENTIALS:
        return ADMIN_CREDENTIALS[username] == password

    # Check user credentials
    if username in USER_CREDENTIALS:
        return USER_CREDENTIALS[username] == password

    return False


def get_user_role(username: str) -> Optional[str]:
    """
    Get the role for a given username.

    Args:
        username: Username to check

    Returns:
        'admin' or 'user' or None if username not found
    """
    if username in ADMIN_CREDENTIALS:
        return "admin"

    if username in USER_CREDENTIALS:
        return "user"

    return None


def get_all_users():
    """
    Get list of all valid usernames (for testing/debugging).

    Returns:
        Dictionary with admin and user lists
    """
    return {
        "admins": list(ADMIN_CREDENTIALS.keys()),
        "users": list(USER_CREDENTIALS.keys())
    }
