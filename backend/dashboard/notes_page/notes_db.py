from utils import get_db_connection
from mysql.connector import Error

def get_notes(email):
    """Fetches all notes for a given user email."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, title, content FROM notes WHERE user_email = %s", (email,))
        notes = cursor.fetchall()
        return notes
    except Error as e:
        print(f"Error fetching notes: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_note(email, title, content):
    """Inserts a new secure note for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (user_email, title, content) VALUES (%s, %s, %s)",
            (email, title, content)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting note: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def verify_ownership(note_id, email):
    """Checks if a secure note record belongs to a specific user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM notes WHERE id = %s AND user_email = %s", (note_id, email))
        exists = cursor.fetchone() is not None
        return exists
    except Error as e:
        print(f"Error checking note ownership: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_note(note_id, email, title, content):
    """Updates an existing secure note."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE notes SET title = %s, content = %s WHERE id = %s AND user_email = %s",
            (title, content, note_id, email)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error updating note: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_note(note_id, email):
    """Deletes a secure note record."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notes WHERE id = %s AND user_email = %s", (note_id, email))
        conn.commit()
        return True
    except Error as e:
        print(f"Error deleting note: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def get_images(email):
    """Fetches all uploaded images for a given user email."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, filename, original_name, created_at FROM user_images WHERE user_email = %s ORDER BY created_at DESC", (email,))
        images = cursor.fetchall()
        return images
    except Error as e:
        print(f"Error fetching images: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_image(email, filename, original_name):
    """Inserts a new image upload record into the database."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_images (user_email, filename, original_name) VALUES (%s, %s, %s)",
            (email, filename, original_name)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting image record: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def verify_image_ownership(image_id, email):
    """Verifies that the requested image belongs to the specified user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT filename FROM user_images WHERE id = %s AND user_email = %s", (image_id, email))
        record = cursor.fetchone()
        return record
    except Error as e:
        print(f"Error checking image ownership: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_image_db(image_id, email):
    """Deletes an image record from the database."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_images WHERE id = %s AND user_email = %s", (image_id, email))
        conn.commit()
        return True
    except Error as e:
        print(f"Error deleting image from database: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()