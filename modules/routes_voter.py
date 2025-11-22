# modules/routes_voter.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from modules.db_utils import get_db_connection
import re

voter_routes = Blueprint('voter_routes', __name__, template_folder='../templates')

def valid_email(email):
    # basic email validation
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@voter_routes.route('/', methods=['GET'])
def index():
    # simple landing -> voter login page (you may already have index elsewhere)
    return render_template('voter/index.html')

@voter_routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        voter_id = request.form.get('voter_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Basic validation
        if not voter_id or not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for('voter_routes.register'))

        if not valid_email(email):
            flash("Please provide a valid email address.", "warning")
            return redirect(url_for('voter_routes.register'))

        conn = get_db_connection()
        cur = conn.cursor()

        # Check duplicate voter_id or email
        existing = cur.execute("SELECT * FROM voters WHERE voter_id=? OR email=?", (voter_id, email)).fetchone()
        if existing:
            conn.close()
            flash("Voter ID or email already registered. Choose a different Voter ID or contact admin.", "danger")
            return redirect(url_for('voter_routes.register'))

        pw_hash = generate_password_hash(password)

        try:
            cur.execute(
                "INSERT INTO voters (voter_id, name, email, password_hash, has_voted) VALUES (?, ?, ?, ?, 0)",
                (voter_id, name, email, pw_hash)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            conn.close()
            flash("An error occurred while registering. Try again.", "danger")
            # optionally log exception somewhere
            return redirect(url_for('voter_routes.register'))

        conn.close()
        flash("Registration successful! Please login to continue.", "success")
        return redirect(url_for('voter_routes.index'))

    # GET
    return render_template('voter/register.html')
