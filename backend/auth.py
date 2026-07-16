from flask import jsonify, session
from mysql.connector import Error
from utils import get_db_connection

def get_user_profile():
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name, email, role, gender, age, phone_number, address FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404
        return jsonify({'status': 'success', 'user': user})
    except Error as e:
        print(f"Error fetching user profile: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to load profile.'}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def logout():
    session.clear()
    return jsonify({'status': 'success', 'redirect': '/'})
