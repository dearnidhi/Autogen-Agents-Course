"""
Sample Python file with intentional bugs for code review demo.
DO NOT use this code in production!
"""

import os
import sqlite3
import pickle


def get_user(user_id):
    # BUG 1: SQL injection vulnerability
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE id = " + user_id  # NEVER do string concatenation
    result = conn.execute(query)
    return result.fetchone()


def process_data(data_list):
    # BUG 2: Off-by-one error + no type check
    result = []
    for i in range(len(data_list) + 1):  # Off by one!
        result.append(data_list[i] * 2)  # IndexError on last iteration
    return result


def load_config(filepath):
    # BUG 3: Insecure deserialization
    with open(filepath, 'rb') as f:
        return pickle.load(f)  # DANGER: arbitrary code execution


def calculate_average(numbers):
    # BUG 4: No zero-division check, no empty list check
    return sum(numbers) / len(numbers)  # ZeroDivisionError if empty


PASSWORD = "admin123"  # BUG 5: Hardcoded credential

def login(username, password):
    if password == PASSWORD:  # BUG 6: No hashing
        return True
    return False


def read_file(filename):
    # BUG 7: Path traversal vulnerability
    with open(filename, 'r') as f:  # Could access ../../../etc/passwd
        return f.read()


def process_users(users):
    # BUG 8: O(n²) complexity — should be O(n)
    result = []
    for user in users:
        for existing in result:  # Quadratic!
            if existing['id'] == user['id']:
                break
        else:
            result.append(user)
    return result
