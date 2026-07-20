from flask import Blueprint, render_template
from registration import verified_otp_page, set_password_page, signup, verify_otp_api, resend_otp_api, set_password_api
from sign_up import login
from auth import get_user_profile, logout
from backend.dashboard.password_Vault_page.Password_Vault import manage_passwords, manage_password_by_id
from backend.dashboard.notes_page.notes import (
    manage_notes,
    manage_note_by_id,
    manage_images,
    delete_image
)

# Define blueprints
main_bp = Blueprint('main', __name__)
registration_bp = Blueprint('registration', __name__)
signup_bp = Blueprint('signup', __name__)
dashboard_bp = Blueprint('dashboard', __name__)

def index():
    return render_template('index.html')

def home():
    return render_template('dashboard/passwords.html')

def notes_page():
    return render_template('dashboard/notes.html')

def note_pic_page():
    return render_template('dashboard/note_pic.html')

# Register HTML/Main routes
main_bp.route('/')(index)
main_bp.route('/home')(home)
main_bp.route('/notes')(notes_page)
main_bp.route('/note-pic')(note_pic_page)

# Register Registration routes
registration_bp.route('/verify-otp')(verified_otp_page)
registration_bp.route('/set-password')(set_password_page)
registration_bp.route('/api/signup', methods=['POST'])(signup)
registration_bp.route('/api/verify-otp', methods=['POST'])(verify_otp_api)
registration_bp.route('/api/resend-otp', methods=['POST'])(resend_otp_api)
registration_bp.route('/api/set-password', methods=['POST'])(set_password_api)

# Register Sign Up/Login routes
signup_bp.route('/api/login', methods=['POST'])(login)

# Dashboard API routes
dashboard_bp.route('/api/user/profile')(get_user_profile)
dashboard_bp.route('/api/passwords', methods=['GET', 'POST'])(manage_passwords)
dashboard_bp.route('/api/passwords/<int:pwd_id>', methods=['PUT', 'DELETE'])(manage_password_by_id)
dashboard_bp.route('/api/notes', methods=['GET', 'POST'])(manage_notes)
dashboard_bp.route('/api/notes/<int:note_id>', methods=['PUT', 'DELETE'])(manage_note_by_id)
dashboard_bp.route('/api/images', methods=['GET', 'POST'])(manage_images)
dashboard_bp.route('/api/images/<int:image_id>', methods=['DELETE'])(delete_image)
dashboard_bp.route('/api/logout', methods=['POST'])(logout)

def register_routes(app):
    """Links and registers all routing blueprints in the project."""
    app.register_blueprint(main_bp)
    app.register_blueprint(registration_bp)
    app.register_blueprint(signup_bp)
    app.register_blueprint(dashboard_bp)
