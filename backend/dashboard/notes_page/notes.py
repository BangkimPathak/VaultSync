from flask import request, jsonify, session
from backend.dashboard.notes_page.notes_db import (
    get_notes,
    insert_note,
    verify_ownership,
    update_note,
    delete_note
)

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
        # Support both 'title'/'content' (frontend) and 'Note Title'/'Secure Content' (user script) keys
        title = (data.get('title') or data.get('Note Title') or '').strip()
        content = (data.get('content') or data.get('Secure Content') or '').strip()
        
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
        content = (data.get('content') or data.get('Secure_Content') or '').strip()
        
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