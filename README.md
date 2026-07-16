# VaultSync - Secure Credential & Notes Manager

VaultSync is a self-hosted secure vault application designed to store login credentials and private notes. It features secure email-based OTP (One-Time Password) registration, SHA-256 account password hashing, and a responsive glassmorphic dashboard interface.

---

## Features

- **OTP Email Registration**: Ensures verified accounts by sending a 6-digit verification code using SMTP. Includes a local mock email fallback printed to the console if SMTP is not configured.
- **Secure Password Hashing**: Hashes master passwords using SHA-256 before storing them in the database.
- **Credential Vault**: Add, edit, delete, search, and toggle visibility of saved website/app credentials. Provides a one-click button to copy usernames or passwords to the clipboard.
- **Secure Notes**: Save, edit, delete, and search private notes or code snippets.
- **Modern Glassmorphic UI**: High-fidelity dashboard featuring responsive CSS grids, sidebar navigation, dark/light theme gradients, glassmorphism overlays, and smooth CSS micro-interactions.

---

## Directory Structure

```text
VaultSync/
├── backend/
│   ├── dashboard/
│   │   ├── Password_app.py   # API endpoints for passwords CRUD
│   │   └── notes.py          # API endpoints for notes CRUD
│   ├── app.py                # Main application entry point (Flask configuration)
│   ├── auth.py               # User session and profile routing
│   ├── registration.py       # OTP generation, verification, and registration routing
│   ├── routes.py             # Route blueprint mappings
│   ├── sign_up.py            # User authentication / login controller
│   └── utils.py              # MySQL init, hash helpers, and SMTP setup
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Design tokens and custom styles
│   │   └── js/
│   │       ├── main.js       # Authentication switching logic
│   │       └── passwords.js  # Modular scripts for Password CRUD and copy functions
│   └── templates/
│       ├── dashboard/
│       │   ├── notes.html     # Secure Notes dashboard view
│       │   └── passwords.html # Passwords dashboard view
│       ├── index.html         # Login / Registration view
│       ├── set_password.html  # Post-verification master password configuration
│       └── verified_otp.html  # OTP verification input screen
├── .env                       # Environment configuration secrets (gitignored)
├── requirements.txt           # Python backend dependencies
└── README.md                  # Project documentation (this file)
```

---

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: MySQL
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism layout), Vanilla JavaScript

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- MySQL Server running locally or remotely.

### 2. Configure Environment Variables
Create a `.env` file in the root directory of the project and populate it with your database and email credentials:

```ini
# SMTP Configuration (For OTP Emails)
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_gmail_app_password

# Database Configuration
DB_HOST=your_host_address
DB_PORT=Your_port_address
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=your_DB_name
```

> [!TIP]
> If `SENDER_EMAIL` or `SENDER_APP_PASSWORD` is left unset, the backend will print the OTP code to the console/terminal as a fallback for local testing.

### 3. Setup Virtual Environment
Run the following commands in your terminal:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Activate virtual environment (macOS/Linux)
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
Start the Flask dev server:
```bash
python backend/app.py
```

The application will run on the linked generated in the terminal . The database and its required tables will be automatically initialized and created on start.
