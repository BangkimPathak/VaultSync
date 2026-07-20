import os
import hashlib
import re
import random
import smtplib
import mysql.connector
from mysql.connector import Error
from email.message import EmailMessage
from dotenv import load_dotenv

# load env
load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_PORT_ENV = os.environ.get("DB_PORT")
DB_PORT = int(DB_PORT_ENV)
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME", "patient_records")

# --- MYSQL DATABASE AND TABLE INITIALIZATION ---
def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )       
    except Error as e:
        print(f"error connecting to mysql: {e}")
        return None
    
# utility help
def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# EMAIL VALIDATION
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def send_smtp_email_raw(from_mail, password, recipient_email, otp):
    """Establishes connection to SMTP server and sends verification mail."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_mail, password)

    message = EmailMessage()
    message['Subject'] = 'ABC Hospital - OTP Verification'
    message['From'] = from_mail
    message['To'] = recipient_email
    message.set_content(
        f'Your verification code is: {otp}\nThis code is strictly for verification purposes and will expire in 10 minutes.'
    )

    server.send_message(message)
    server.quit()

#OTP EMAIL SENDING 
def send_otp_email(recipient_email, otp):
    from_mail = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("SENDER_APP_PASSWORD")
    # Check if the email and password are configured
    if not from_mail or not password or "your_email" in from_mail or "your_app" in password:
        print("\n" + "="*60)
        print(" [WARNING] SENDER_EMAIL or SENDER_APP_PASSWORD not configured in .env!")
        print(f" OTP for {recipient_email} is: {otp}")
        print("="*60 + "\n")
        return
    # SMTP EMAIL SENDING
    try:
        send_smtp_email_raw(from_mail, password, recipient_email, otp)
        print(f"[SMTP SUCCESS] Verification code email sent to {recipient_email}")
    except Exception as e:
        print(f"[SMTP ERROR] Failed to send email to {recipient_email}: {e}")
        print(f"[MOCK EMAIL FALLBACK] OTP code for {recipient_email} is: {otp}")

def create_database_tables(cursor):
    """Creates the user registration and visitor tables if they do not exist."""
    # Create permanent users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            gender enum("Male", "Female" , "Other") NOT NULL, 
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL,
            age INT NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            address VARCHAR(255) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'Unverified',
            is_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # otp table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp (
            email VARCHAR(100) PRIMARY KEY,
            otp VARCHAR(6) NOT NULL,
            attempts INT DEFAULT 0,
            status VARCHAR(20) DEFAULT 'Unverified',
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Check and migrate notes table if legacy
    cursor.execute("SHOW TABLES LIKE 'notes'")
    if cursor.fetchone():
        cursor.execute("SHOW COLUMNS FROM notes LIKE 'user_email'")
        if not cursor.fetchone():
            cursor.execute("DROP TABLE notes")

    # Check and migrate save_passwords table if legacy
    cursor.execute("SHOW TABLES LIKE 'save_passwords'")
    if cursor.fetchone():
        cursor.execute("SHOW COLUMNS FROM save_passwords LIKE 'user_email'")
        if not cursor.fetchone():
            cursor.execute("DROP TABLE save_passwords")

    # Clean up old redundant passwords table
    cursor.execute("DROP TABLE IF EXISTS passwords")

    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100) NOT NULL,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)

    # Create save_passwords table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS save_passwords (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100) NOT NULL,
            website_name VARCHAR(255) NOT NULL,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)

    # Create user_images table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_email VARCHAR(100) NOT NULL,
            filename VARCHAR(255) NOT NULL,
            original_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        )
    """)


def init_db():
    """Initializes the MySQL database and tables if they do not exist."""
    connection = None
    try:
        # First connect without a database specified to create it if missing
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            cursor.close()
            connection.close()

        # Now connect to the database and create tables
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            cursor = connection.cursor()
            create_database_tables(cursor)
            cursor.close()
            print("[DB INITIALIZED] MySQL database and tables verified/created successfully.")
    except Error as e:
        print(f"[DB INITIALIZATION ERROR] Failed to initialize database: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()