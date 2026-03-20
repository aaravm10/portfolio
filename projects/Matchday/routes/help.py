"""
Help Page Route - FAQ and Contact Form
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime
from utils.auth import get_current_user

help_bp = Blueprint('help', __name__, url_prefix='/help')


@help_bp.route('/')
def help_page():
    """Display help page with FAQ"""
    
    # FAQ data organized by category
    faqs = {
        'General': [
            {
                'question': 'Is MATCHDAY free to use?',
                'answer': 'Yes! MATCHDAY is completely free. You can create an account to access personalized features like watchlists and custom teams.'
            },
            {
                'question': 'How often is the data updated?',
                'answer': 'Player statistics are updated after each gameweek, typically within 24 hours of matches finishing. Live gameweek data refreshes every few hours during matchdays.'
            },
        ],
        'Features': [
            {
                'question': 'What is the Team of the Week?',
                'answer': 'Our TOTW feature uses a custom algorithm to select the best-performing 11 players from each gameweek based on goals, assists, clean sheets, and advanced performance metrics like influence, creativity, and threat.'
            },
            {
                'question': 'How do Leaderboards work?',
                'answer': 'Leaderboards rank players and teams across various metrics. Player rankings use FPL data for goals, assists, xG, xA, clean sheets, and saves. Team rankings combine FPL aggregates with API-Football stats for advanced metrics like goals per game, win rate, and discipline.'
            },
            {
                'question': 'What is the Create Team feature?',
                'answer': 'Create Team lets you build your own custom XI by selecting players from any Premier League team. You can view their combined stats and save your formations for future reference.'
            },
            {
                'question': 'How does the Best XI Optimizer work?',
                'answer': 'The Optimizer builds the highest-scoring XI within your budget using FPL points and value metrics. Set your budget (£60m-£110m), choose a formation, and it will select the optimal 11 players with max 3 per club and minimum minutes played.'
            },
            {
                'question': 'What is Fixture Difficulty Rating (FDR)?',
                'answer': 'FDR shows upcoming fixture difficulty for each team on a 1-5 scale. Green (1-2) means easier fixtures, yellow (3) is medium, and red (4-5) indicates tough matches. Use this to plan transfers and captain choices.'
            },
            {
                'question': 'How does the Match Predictor work?',
                'answer': 'The Match Predictor uses season-average xG (expected goals) data to forecast match outcomes. It analyzes each team\'s attacking and defensive strength to predict the likely winner with confidence levels (low, medium, high).'
            },
            {
                'question': 'How does the Watchlist work?',
                'answer': 'The Watchlist allows you to save and track your favorite players. You need to be logged in to use this feature. Click the star icon on any player card in the Dashboard to add them. Your watchlist persists across sessions so you can monitor player form over time.'
            },
        ],
        'Data & Stats': [
            {
                'question': 'What do xG and xA mean?',
                'answer': 'xG (expected goals) measures the quality of a chance based on factors like distance and angle. xA (expected assists) measures the likelihood a pass leads to a goal. Higher values indicate better quality chances created or received.'
            },
            {
                'question': 'What is the ICT Index?',
                'answer': 'ICT Index combines Influence (impact on match result), Creativity (chance creation), and Threat (likelihood to score). It\'s FPL\'s way of measuring overall player performance beyond just goals and assists.'
            },
            {
                'question': 'How accurate is the Match Predictor?',
                'answer': 'The Match Predictor uses season-average xG data and is most accurate for established team patterns. Confidence levels indicate prediction reliability: high confidence means a significant xG difference, while low confidence suggests an even matchup.'
            },
            {
                'question': 'What metrics are used in the Optimizer?',
                'answer': 'The Best XI Optimizer prioritizes FPL total points and points-per-cost value. It requires players to have played at least 450 minutes and enforces a maximum of 3 players per club to ensure squad diversity.'
            },
            {
                'question': 'Can I export player statistics?',
                'answer': 'Currently, data export is not available, but we\'re considering adding CSV/Excel export functionality in future updates.'
            },
        ],
        'Account': [
            {
                'question': 'Do I need an account to use MATCHDAY?',
                'answer': 'No, you can browse player stats, leaderboards, and TOTW without an account. However, creating an account unlocks features like Watchlist and saved custom teams.'
            },
            {
                'question': 'How do I reset my password?',
                'answer': 'Click "Forgot Password" on the login page and enter your email. We\'ll send you a link to reset your password.'
            },
            {
                'question': 'Can I delete my account?',
                'answer': 'Yes, contact us through the form below and we\'ll process your account deletion request within 48 hours.'
            },
        ],
    }
    
    current_user = get_current_user()
    return render_template('help.html', faqs=faqs, current_user=current_user)


@help_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Handle contact form submission"""
    
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()
    
    # Basic validation
    if not all([name, email, subject, message]):
        flash('Please fill in all fields.', 'error')
        return redirect(url_for('help.help_page'))
    
    if '@' not in email:
        flash('Please enter a valid email address.', 'error')
        return redirect(url_for('help.help_page'))
    
    # Dummy form submission - can be extended to save to database or send email notifications
    
    # Log the submission
    submission = {
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"Contact form submission: {submission}")
    
    flash('Thank you for your message! We\'ll get back to you within 24-48 hours.', 'success')
    return redirect(url_for('help.help_page'))