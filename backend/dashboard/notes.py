from flask import request, jsonify, session
from mysql.connector import Error
from utils import get_db_connection

def manage_notes():
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
            cursor.execute("SELECT id, title, content FROM notes WHERE user_email = %s", (email,))
            notes = cursor.fetchall()
            return jsonify({'status': 'success', 'notes': notes}), 200
        except Error as e:
            print(f"Error fetching notes: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to fetch notes.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()
            
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
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO notes (user_email, title, content) VALUES (%s, %s, %s)",
                (email, title, content)
            )
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Note successfully saved.'}), 200
        except Error as e:
            print(f"Error inserting note: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to save note.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

def manage_note_by_id(note_id):
    email = session.get('user_email')
    if not email:
        return jsonify({'status': 'error', 'message': 'Unauthorized.'}), 401
        
    conn = None
    cursor = None
    
    if request.method == 'PUT':
        data = request.get_json() or {}
        title = (data.get('title') or data.get('Note Title') or '').strip()
        content = (data.get('content') or data.get('Secure Content') or '').strip()
        
        if not title or not content:
            return jsonify({'status': 'error', 'message': 'Title and content are required.'}), 400
            
        if len(title) > 20:
            return jsonify({'status': 'error', 'message': 'Title must contain less than 20 letters.'}), 400
            
        try:
            conn = get_db_connection()
            if conn is None:
                return jsonify({'status': 'error', 'message': 'Database connection failed.'}), 500
            cursor = conn.cursor()
            # Verify ownership
            cursor.execute("SELECT id FROM notes WHERE id = %s AND user_email = %s", (note_id, email))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Note not found or unauthorized.'}), 404
                
            cursor.execute(
                "UPDATE notes SET title = %s, content = %s WHERE id = %s AND user_email = %s",
                (title, content, note_id, email)
            )
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Note updated successfully!'}), 200
        except Error as e:
            print(f"Error updating note: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to update note.'}), 500
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
            cursor.execute("SELECT id FROM notes WHERE id = %s AND user_email = %s", (note_id, email))
            if not cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Note not found or unauthorized.'}), 404
                
            cursor.execute("DELETE FROM notes WHERE id = %s AND user_email = %s", (note_id, email))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'Note deleted successfully!'}), 200
        except Error as e:
            print(f"Error deleting note: {e}")
            return jsonify({'status': 'error', 'message': 'Failed to delete note.'}), 500
        finally:
            if cursor: cursor.close()
            if conn: conn.close()