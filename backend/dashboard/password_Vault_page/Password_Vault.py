from flask import request, jsonify, session
from backend.dashboard.password_Vault_page.pasword_db import (
    get_passwords,
    insert_password,
    verify_ownership,
    update_password,
    delete_password
)

def manage_passwords():
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
    
    if request.method == 'GET':
        try:
            passwords = get_passwords(email)
            return jsonify({'status': 'success', 'passwords': passwords}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to fetch passwords.'}), 500
            
    elif request.method == 'POST':
        data = request.get_json() or {}
        # Support both 'website_name'/'username' (frontend) and 'Website or Applicatione'/'Username / Email' (user script) keys
        website_name =  (data.get('website_name')  or '').strip()
        username =      (data.get('username') or '').strip()
        password =      (data.get('password') or '').strip()
        
        if not website_name or not username or not password:
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
            
        if len(website_name) > 50:
            return jsonify({'status': 'error', 'message': 'Website_name must contain less than 50 letters.'}), 400
            
        try:
            insert_password(email, website_name, username, password)
            return jsonify({'status': 'success', 'message': 'Password successfully saved.'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to save credential.'}), 500

def manage_password_by_id(pwd_id):
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
        
    if request.method == 'PUT':
        data = request.get_json() or {}
        website_name = (data.get('website_name') or  '').strip()
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()
        
        if not website_name or not username or not password:
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400
            
        if len(website_name) > 50:
            return jsonify({'status': 'error', 'message': 'Website_name must contain less than 50 letters.'}), 400
               
        try:
            # Verify ownership first
            if not verify_ownership(pwd_id, email):
                return jsonify({'status': 'error', 'message': 'Credential not found or unauthorized.'}), 404
                
            update_password(pwd_id, email, website_name, username, password)
            return jsonify({'status': 'success', 'message': 'Credential updated successfully!'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to update credential.'}), 500
            
    elif request.method == 'DELETE':
        try:
            # Verify ownership first
            if not verify_ownership(pwd_id, email):
                return jsonify({'status': 'error', 'message': 'Credential not found or unauthorized.'}), 404
                
            delete_password(pwd_id, email)
            return jsonify({'status': 'success', 'message': 'Credential deleted successfully!'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to delete credential.'}), 500