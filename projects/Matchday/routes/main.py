from flask import Blueprint, render_template
from utils.auth import get_current_user
from utils.charts import get_3d_model_base64

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    """Home page route"""
    current_user = get_current_user()
    glb_data = get_3d_model_base64()
    
    return render_template('index.html', 
                         current_user=current_user,
                         glb_data=glb_data)

@main_bp.route('/about')
def about():
    """About page route"""
    current_user = get_current_user()
    
    return render_template('about.html', 
                         current_user=current_user)