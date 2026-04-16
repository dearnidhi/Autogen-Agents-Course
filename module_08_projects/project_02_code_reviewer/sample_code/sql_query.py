"""
Sample code: Database query functions with multiple issues.
Security reviewer targets: SQL injection, hardcoded credentials, unsafe practices.
"""

import sqlite3
import os
import hashlib
import random  # Should use secrets for security-sensitive operations


# CRITICAL: Hardcoded database credentials
DB_HOST = "prod-db.company.com"
DB_PORT = 5432
DB_NAME = "production_users"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret123!"  # SECURITY: Never hardcode passwords!
API_KEY = "sk-proj-abc123xyz456"  # SECURITY: Exposed API key!


def get_user(username: str):
    """
    SECURITY ISSUE: SQL injection vulnerability.
    User input is directly interpolated into the SQL query.
    Attacker input: username = "admin' OR '1'='1"
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # CRITICAL: String formatting in SQL = SQL injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    result = cursor.fetchone()
    conn.close()  # ISSUE: Should use context manager (with statement)
    return result


def search_products(category: str, min_price: float, max_price: float):
    """Another SQL injection vulnerability using string concatenation."""
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    # CRITICAL: Multiple injection points
    query = ("SELECT * FROM products WHERE category = '" + category +
             "' AND price BETWEEN " + str(min_price) +
             " AND " + str(max_price))

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


def delete_user(user_id):
    """
    HIGH: No authentication check before destructive operation.
    HIGH: SQL injection in DELETE statement.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # No check: is the caller authorized to delete users?
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
    conn.commit()
    conn.close()
    print(f"Deleted user {user_id}")  # MEDIUM: Logging sensitive operations to stdout


def create_session_token(user_id: int) -> str:
    """
    SECURITY: Using random instead of secrets for security tokens.
    random is not cryptographically secure.
    """
    # WRONG: random.randint is predictable
    token = str(random.randint(100000, 999999))
    return f"{user_id}:{token}"


def hash_password(password: str) -> str:
    """
    SECURITY: MD5 is cryptographically broken.
    Should use bcrypt, argon2, or at minimum SHA-256 with salt.
    """
    # CRITICAL: MD5 is not suitable for password hashing
    return hashlib.md5(password.encode()).hexdigest()


def get_admin_users():
    """
    MEDIUM: Selecting all columns when only a few are needed.
    MEDIUM: No pagination — could return millions of rows.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Should use parameterized query even for constants
    # Should select only needed columns
    # Should add LIMIT clause
    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    return cursor.fetchall()
    # ISSUE: Connection never closed — resource leak!


def update_user_email(user_id: int, new_email: str):
    """
    SECURITY: SQL injection in UPDATE.
    MEDIUM: No email format validation.
    MEDIUM: No check that user_id exists before updating.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # CRITICAL: String interpolation in UPDATE query
    cursor.execute(f"UPDATE users SET email = '{new_email}' WHERE id = {user_id}")
    conn.commit()

    # Logging PII to console
    print(f"Updated email for user {user_id} to {new_email}")
    conn.close()


def bulk_insert_users(users: list):
    """
    MEDIUM: Building INSERT query by string concatenation.
    MEDIUM: No transaction handling — partial inserts on failure.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    for user in users:
        # SECURITY: SQL injection in bulk insert
        query = f"INSERT INTO users (name, email) VALUES ('{user['name']}', '{user['email']}')"
        cursor.execute(query)

    conn.commit()
    conn.close()
