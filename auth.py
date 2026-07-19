"""
auth.py — User registration, login, and session state management.
"""
import bcrypt
import streamlit as st
from database import fetch_one, execute_returning


# ─── Password helpers ─────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ─── Session helpers ──────────────────────────────────────────────────────────
def is_logged_in() -> bool:
    return st.session_state.get("user_id") is not None


def get_current_user() -> dict | None:
    uid = st.session_state.get("user_id")
    if uid is None:
        return None
    return fetch_one("SELECT * FROM users WHERE id = %s;", (uid,))


def login_user(user: dict) -> None:
    st.session_state["user_id"] = user["id"]
    st.session_state["user_name"] = user["name"]
    st.session_state["user_email"] = user["email"]
    st.session_state["page"] = "home"


def logout_user() -> None:
    for key in ["user_id", "user_name", "user_email", "page",
                "search_results", "selected_bus", "selected_seats"]:
        st.session_state.pop(key, None)


# ─── Registration ─────────────────────────────────────────────────────────────
def register_user(name: str, email: str, password: str,
                  contact: str, dob, gender: str) -> tuple[bool, str]:
    """
    Returns (success: bool, message: str).
    """
    existing = fetch_one("SELECT id FROM users WHERE email = %s;", (email,))
    if existing:
        return False, "An account with this email already exists."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    pw_hash = hash_password(password)
    dob_val = dob if dob else None

    try:
        row = execute_returning(
            """
            INSERT INTO users (name, email, password_hash, contact, dob, gender)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (name, email, pw_hash, contact, dob_val, gender),
        )
        login_user(row)
        return True, f"Welcome, {name}! Your account has been created."
    except Exception as e:
        return False, f"Registration failed: {e}"


# ─── Login ────────────────────────────────────────────────────────────────────
def authenticate_user(email: str, password: str) -> tuple[bool, str]:
    """
    Returns (success: bool, message: str).
    """
    user = fetch_one("SELECT * FROM users WHERE email = %s;", (email,))
    if not user:
        return False, "No account found with this email."

    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password. Please try again."

    login_user(user)
    return True, f"Welcome back, {user['name']}!"
