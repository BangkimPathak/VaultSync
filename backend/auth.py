import os
# import uuid
from flask import jsonify, session, request
from mysql.connector import Error
from utils import get_db_connection

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static', 'uploads'))

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def logout():
    session.clear()
    return jsonify({
        "status": "success",
        "redirect": "/"
    })
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
        
        cursor.execute("SHOW COLUMNS FROM users LIKE 'alt_email'")
        has_alt = cursor.fetchone()
        cursor.execute("SHOW COLUMNS FROM users LIKE 'dob'")
        has_dob = cursor.fetchone()

        select_fields = [
            "name", "email", "gender", "age", "phone_number", "address",
            "DATE_FORMAT(created_at, '%b %d, %Y') AS created_at"
        ]
        if has_alt:
            select_fields.append("alt_email")
        if has_dob:
            select_fields.append("DATE_FORMAT(dob, '%Y-%m-%d') AS dob")

        query = f"SELECT {', '.join(select_fields)} FROM users WHERE email = %s"
        cursor.execute(query, (email,))
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

def update_user_profile():
    email = session.get('user_email')

    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401

    name = request.form.get('name')
    age = request.form.get('age')
    phone_number = request.form.get('phone_number')
    alt_email = request.form.get('alt_email', '')
    dob = request.form.get('dob', '')

    if not age or not phone_number:
        return jsonify({
            'status': 'error',
            'message': 'Age and phone number are required.'
        }), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()

        if conn is None:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed.'
            }), 500

        cursor = conn.cursor()

        cursor.execute("SHOW COLUMNS FROM users LIKE 'alt_email'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN alt_email VARCHAR(100) DEFAULT NULL")

        cursor.execute("SHOW COLUMNS FROM users LIKE 'dob'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE users ADD COLUMN dob DATE DEFAULT NULL")

        cursor.execute(
            """
            UPDATE users
            SET
                name = %s,
                age = %s,
                phone_number = %s,
                alt_email = %s,
                dob = %s
            WHERE email = %s
            """,
            (name, age, phone_number, alt_email, dob if dob else None, email)
        )

        conn.commit()

        return jsonify({
            'status': 'success',
            'message': 'Profile updated successfully.'
        })

    except Error as e:
        print(f"Error updating user profile: {e}")

        return jsonify({
            'status': 'error',
            'message': 'Failed to update profile.'
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()