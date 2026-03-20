from flask import session
from functools import wraps
from models.user import get_user_by_username

def login_required(f):
    """Decorator to require login for a view"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current logged-in user"""
    if 'username' in session:
        return get_user_by_username(session['username'])
    return None

def is_logged_in():
    """Check if user is logged in"""
    return 'user_id' in session and 'username' in session

def login_user(user):
    """Log in a user by setting session variables"""
    session['user_id'] = user['id']
    session['username'] = user['name']
    session.permanent = True

def logout_user():
    """Log out the current user"""
    session.clear()

def get_user_display_name():
    """Get the display name of the current user"""
    if 'username' in session:
        return session['username']
    return None