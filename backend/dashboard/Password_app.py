from flask import request, jsonify, session
from mysql.connector import Error
from utils import get_db_connection

def manage_passwords():
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
    
    conn = None
    cursor = None
    
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, website_name, username, password FROM save_passwords WHERE user_email = %s", (email,))
            passwords = cursor.fetchall()
            return jsonify({'status': 'success', 'passwords': passwords}), 200
        except Error as e:
            print(f"Error fetching passwords: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch passwords.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    elif request.method == 'POST':
        data = request.get_json() or {}
        # Support both 'website_name'/'username' (frontend) and 'Website or Applicatione'/'Username / Email' (user script) keys
        website_name = (data.get('website_name') or data.get('Website or Applicatione') or '').strip()
        username = (data.get('username') or data.get('Username / Email') or '').strip()
        password = (data.get('password') or '').strip()
        conform_password = (data.get(' Conform password') or '').strip()
        
        if not website_name or not username or not password:
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
            
        if len(website_name) > 50:
            return jsonify({'status': 'error', 'message': 'Website_name must contain less than 50 letters.'}), 400
            
        if conform_password and password != conform_password:
            return jsonify({'status': 'error', 'message': 'Passwords must be the same.'}), 400
            
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO save_passwords (user_email, website_name, username, password) VALUES (%s, %s, %s, %s)",
                (email, website_name, username, password)
            )
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Password successfully saved.'}), 200
        except Error as e:
            print(f"Error inserting password: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to save credential.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

def manage_password_by_id(pwd_id):
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
        
    conn = None
    cursor = None
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        website_name = (data.get('website_name') or data.get('Website or Applicatione') or '').strip()
        username = (data.get('username') or data.get('Username / Email') or '').strip()
        password = (data.get('password') or '').strip()
        conform_password = (data.get(' Conform password') or '').strip()
        
        if not website_name or not username or not password:
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
            
        if len(website_name) > 50:
            return jsonify({'status': 'error', 'message': 'Website_name must contain less than 50 letters.'}), 400
            
        if conform_password and password != conform_password:
            return jsonify({'status': 'error', 'message': 'Passwords must be the same.'}), 400
            
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            # Verify ownership first
            cursor.execute("SELECT id FROM save_passwords WHERE id = %s AND user_email = %s", (pwd_id, email))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Credential not found or unauthorized.'}), 404
                
            cursor.execute(
                "UPDATE save_passwords SET website_name = %s, username = %s, password = %s WHERE id = %s AND user_email = %s",
                (website_name, username, password, pwd_id, email)
            )
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Credential updated successfully!'}), 200
        except Error as e:
            print(f"Error updating password: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to update credential.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
    elif request.method == 'DELETE':
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            # Verify ownership
            cursor.execute("SELECT id FROM save_passwords WHERE id = %s AND user_email = %s", (pwd_id, email))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Credential not found or unauthorized.'}), 404
                
            cursor.execute("DELETE FROM save_passwords WHERE id = %s AND user_email = %s", (pwd_id, email))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Credential deleted successfully!'}), 200
        except Error as e:
            print(f"Error deleting password: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to delete credential.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()