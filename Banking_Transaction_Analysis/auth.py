
import hashlib
import secrets
import hmac
from database import get_connection


# ==========================================
# PASSWORD HASHING
# ==========================================

def hash_password(password):
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return salt + "$" + password_hash


# ==========================================
# PASSWORD VERIFICATION
# ==========================================

def verify_password(password, stored_password):
    try:
        salt, original_hash = stored_password.split("$")

        new_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000
        ).hex()

        return hmac.compare_digest(
            new_hash,
            original_hash
        )

    except (ValueError, AttributeError):
        return False


# ==========================================
# USER REGISTRATION
# ==========================================

def register_user(full_name, email, password):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Check whether email already exists
        cursor.execute(
            "SELECT user_id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return False, "Email already registered!"

        # Hash the password
        password_hash = hash_password(password)

        # Insert new user
        cursor.execute(
            """
            INSERT INTO users
            (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash)
        )

        connection.commit()

        return True, "Registration successful!"

    except Exception as e:
        if connection:
            connection.rollback()

        return False, f"Registration failed: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# ==========================================
# USER LOGIN
# ==========================================

def login_user(email, password):

    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Get user details using email
        cursor.execute(
            """
            SELECT user_id, full_name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        # Verify password
        if user and verify_password(
            password,
            user["password_hash"]
        ):
            return True, user

        return False, "Invalid email or password!"

    except Exception as e:
        return False, f"Login failed: {e}"

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
