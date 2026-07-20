import os
import uuid
from flask import request, jsonify, session
from backend.dashboard.notes_page.notes_db import (
    get_notes,
    insert_note,
    verify_ownership,
    update_note,
    delete_note,
    get_images,
    insert_image,
    verify_image_ownership,
    delete_image_db
)

# Upload directory configuration
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'frontend', 'static', 'uploads'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def manage_notes():
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
        
    if request.method == 'GET':
        try:
            notes = get_notes(email)
            return jsonify({'status': 'success', 'notes': notes}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to fetch secure notes.'}), 500
            
    elif request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        
        if not title or not content:
            return jsonify({'status': 'error', 'message': 'Title and content are required.'}), 400
            
        if len(title) > 20:
            return jsonify({'status': 'error', 'message': 'Title must contain less than 20 letters.'}), 400
            
        try:
            insert_note(email, title, content)
            return jsonify({'status': 'success', 'message': 'Note successfully saved.'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to save note.'}), 500

def manage_note_by_id(note_id):
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
        
    if request.method == 'PUT':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()
        content = (data.get('content') or '').strip()
        
        if not title or not content:
            return jsonify({'status': 'error', 'message': 'Title and content are required.'}), 400
            
        if len(title) > 20:
            return jsonify({'status': 'error', 'message': 'Title must contain less than 20 letters.'}), 400
            
        try:
            # Verify ownership first
            if not verify_ownership(note_id, email):
                return jsonify({'status': 'error', 'message': 'Note not found or unauthorized.'}), 404
                
            update_note(note_id, email, title, content)
            return jsonify({'status': 'success', 'message': 'Note updated successfully!'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to update note.'}), 500
            
    elif request.method == 'DELETE':
        try:
            # Verify ownership first
            if not verify_ownership(note_id, email):
                return jsonify({'status': 'error', 'message': 'Note not found or unauthorized.'}), 404
                
            delete_note(note_id, email)
            return jsonify({'status': 'success', 'message': 'Note deleted successfully!'}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to delete note.'}), 500

# ==============================================================================
# SECURE IMAGES CONTROLLER (File System and Upload Logic)
# ==============================================================================

def manage_images():
    """
    Handles GET (fetching images list) and POST (uploading new image) requests.
    """
    # 1. Authenticate user from session
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401

    # --- GET: Fetch Image List ---
    if request.method == 'GET':
        try:
            # Query MySQL for all uploaded images belonging to this user
            images = get_images(email)
            return jsonify({'status': 'success', 'images': images}), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': 'Failed to fetch secure images.'}), 500

    # --- POST: Upload Image File ---
    elif request.method == 'POST':
        # Validate that the file payload is part of the request
        if 'file' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file part in request.'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected.'}), 400

        # Validate that the extension is allowed (png, jpg, jpeg, gif, webp)
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Allowed file types are png, jpg, jpeg, gif, webp.'}), 400

        try:
            # Ensure static/uploads folder exists on local computer disk
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Secure / generate a randomized UUID filename to prevent collisions and path attacks
            ext = file.filename.rsplit('.', 1)[1].lower()
            random_filename = f"{uuid.uuid4().hex}.{ext}" # E.g., 'a5f82b...png'
            file_path = os.path.join(UPLOAD_FOLDER, random_filename)
            
            # Save the physical image file to disk
            file.save(file_path)
            
            # Insert the description mapping record into MySQL database
            insert_image(email, random_filename, file.filename)
            
            return jsonify({'status': 'success', 'message': 'Image successfully uploaded.'}), 200
        except Exception as e:
            print(f"Error during file upload: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to upload image.'}), 500

def delete_image(image_id):
    """
    Handles DELETE requests to remove an uploaded image from both disk and DB.
    """
    # 1. Authenticate user from session
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401

    if request.method == 'DELETE':
        try:
            # 2. Check ownership first (make sure the user owns the image they're trying to delete)
            record = verify_image_ownership(image_id, email)
            if not record:
                return jsonify({'status': 'error', 'message': 'Image not found or unauthorized.'}), 404
                
            filename = record['filename']
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 3. Delete the physical file from local computer disk
            if os.path.exists(file_path):
                os.remove(file_path)
                
            # 4. Remove metadata record from MySQL database
            delete_image_db(image_id, email)
            
            return jsonify({'status': 'success', 'message': 'Image successfully deleted.'}), 200
        except Exception as e:
            print(f"Error during file deletion: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to delete image.'}), 500