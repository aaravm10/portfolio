from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models.user import authenticate_user, register_user
from utils.auth import login_user, logout_user, get_current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        if request.is_json:
            # Handle AJAX request
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            # Handle form submission
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        
        user = authenticate_user(username, password)
        if user:
            login_user(user)
            if request.is_json:
                return jsonify({'success': True, 'message': f'Welcome, {username}!'})
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('main.home'))
        else:
            error_msg = 'Invalid username or password'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg})
            flash(error_msg, 'error')
    
    current_user = get_current_user()
    return render_template('auth/login.html', current_user=current_user)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        if request.is_json:
            # Handle AJAX request
            data = request.get_json()
            username = data.get('username', '').strip()
            password = data.get('password', '').strip()
        else:
            # Handle form submission
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
        
        success, message = register_user(username, password)
        
        if request.is_json:
            return jsonify({'success': success, 'message': message})
        
        if success:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'error')
    
    current_user = get_current_user()
    return render_template('auth/register.html', current_user=current_user)

@auth_bp.route('/logout')
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))