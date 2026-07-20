from utils import get_db_connection
from mysql.connector import Error

def get_passwords(email):
    """Fetches all passwords for a given user email."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, website_name, username, password FROM save_passwords WHERE user_email = %s", (email,))
        passwords = cursor.fetchall()
        return passwords
    except Error as e:
        print(f"Error fetching passwords: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def insert_password(email, website_name, username, password):
    """Inserts a new password credential for a user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO save_passwords (user_email, website_name, username, password) VALUES (%s, %s, %s, %s)",
            (email, website_name, username, password)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error inserting password: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def verify_ownership(pwd_id, email):
    """Checks if a password record belongs to a specific user."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM save_passwords WHERE id = %s AND user_email = %s", (pwd_id, email))
        exists = cursor.fetchone() is not None
        return exists
    except Error as e:
        print(f"Error checking password ownership: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def update_password(pwd_id, email, website_name, username, password):
    """Updates an existing password credential."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE save_passwords SET website_name = %s, username = %s, password = %s WHERE id = %s AND user_email = %s",
            (website_name, username, password, pwd_id, email)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error updating password: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

def delete_password(pwd_id, email):
    """Deletes a password record."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise Exception("Database connection failed.")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM save_passwords WHERE id = %s AND user_email = %s", (pwd_id, email))
        conn.commit()
        return True
    except Error as e:
        print(f"Error deleting password: {e}")
        raise e
    finally:
        if cursor: cursor.close()
        if conn: conn.close()