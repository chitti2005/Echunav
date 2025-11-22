# voter_app.py
import os
import time
import random
import string
import sqlite3
import smtplib
import re

from email.mime.text import MIMEText
from fpdf import FPDF

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------------------
# App config
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'super_secret_key_here')

DB_PATH = 'database.db'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_IMAGE_EXT = {'png', 'jpg', 'jpeg', 'gif'}

# ---------------------------
# Helpers
# ---------------------------
def db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def send_otp_email(receiver_email, otp):
    sender_email = os.environ.get('SMTP_SENDER')
    password = os.environ.get('SMTP_PASSWORD')
    subject = "E-Chunav OTP Verification"
    body = f"Your OTP for E-Chunav login is: {otp}\n\n(This OTP is valid for this session.)"

    if sender_email and password:
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = receiver_email

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            server.quit()
            print(f"✅ OTP sent to {receiver_email}")
            return True
        except Exception as e:
            print("⚠️ Email send failed:", e)
            return False
    else:
        print(f"🔑 Dev OTP for {receiver_email}: {otp}")
        return False

def is_election_open():
    conn = db_connection()
    try:
        row = conn.execute("SELECT status FROM election_status WHERE id=1").fetchone()
        status = row['status'] if row else 'CLOSED'
    except:
        status = 'CLOSED'
    finally:
        conn.close()
    return status == 'OPEN'

def save_log(action, user_id=None, ip=None):
    try:
        conn = db_connection()
        conn.execute("INSERT INTO logs (action, user_id, ip_address) VALUES (?, ?, ?)",
                     (action, user_id, ip))
        conn.commit()
    except:
        pass
    finally:
        conn.close()

def ensure_election_status_row():
    conn = db_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO election_status (id, status) VALUES (1, 'OPEN')")
        conn.commit()
    finally:
        conn.close()

ensure_election_status_row()

# ---------------------------
# Voter Routes
# ---------------------------

@app.route('/')
def index():
    captcha_num = random.randint(1000, 9999)
    session['captcha_num'] = captcha_num
    return render_template('voter/index.html', captcha_num=captcha_num)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        voter_id = request.form.get('voter_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not all([voter_id, name, email, password]):
            flash("All fields are required.", "warning")
            return redirect(url_for('register'))

        if not valid_email(email):
            flash("Enter a valid email.", "warning")
            return redirect(url_for('register'))

        conn = db_connection()
        try:
            existing = conn.execute("SELECT 1 FROM voters WHERE voter_id=? OR email=?", (voter_id, email)).fetchone()
            if existing:
                flash("Voter ID or email already exists.", "danger")
                return redirect(url_for('register'))

            pw_hash = generate_password_hash(password)
            conn.execute("INSERT INTO voters (voter_id, name, email, password_hash, has_voted) VALUES (?, ?, ?, ?, 0)",
                         (voter_id, name, email, pw_hash))
            conn.commit()
            flash("Registration successful!", "success")
        except Exception as e:
            conn.rollback()
            print("Registration error:", e)
            flash("Registration failed.", "danger")
        finally:
            conn.close()

        return redirect(url_for('index'))
    return render_template('voter/register.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    voter_id = request.form.get('voter_id').strip()
    password = request.form.get('password')
    captcha_answer = request.form.get('captcha_answer')

    if str(session.get('captcha_num')) != str(captcha_answer):
        flash("Incorrect CAPTCHA.", "warning")
        return redirect(url_for('index'))

    conn = db_connection()
    voter = conn.execute("SELECT * FROM voters WHERE voter_id=?", (voter_id,)).fetchone()
    conn.close()

    if not voter or not check_password_hash(voter['password_hash'], password):
        flash("Invalid login credentials.", "danger")
        return redirect(url_for('index'))

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['otp_voter'] = voter_id
    session['resend_count'] = 0

    # Log OTP attempt
    try:
        conn = db_connection()
        conn.execute("INSERT INTO otp_log (voter_id, email, otp) VALUES (?, ?, ?)",
                     (voter_id, voter['email'], otp))
        conn.commit()
    finally:
        conn.close()

    send_otp_email(voter['email'], otp)
    return render_template('voter/otp_verify.html')

@app.route('/resend_otp', methods=['POST'])
def resend_otp():
    if 'otp_voter' not in session:
        flash("Session expired.", "warning")
        return redirect(url_for('index'))

    if session['resend_count'] >= 2:
        flash("Resend limit reached.", "warning")
        return redirect(url_for('index'))

    voter_id = session['otp_voter']

    conn = db_connection()
    voter = conn.execute("SELECT email FROM voters WHERE voter_id=?", (voter_id,)).fetchone()
    conn.close()

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['resend_count'] += 1

    send_otp_email(voter['email'], otp)
    return render_template('voter/otp_verify.html')

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered = request.form.get('otp', '').strip()

    if session.get('otp') == entered:
        voter_id = session.get('otp_voter')
        user_ip = request.remote_addr

        save_log("login", voter_id, user_ip)

    session['voter_id'] = voter_id
    session.pop('otp')
    session.pop('otp_voter')
    session.pop('resend_count')
    # Render the vote page directly after verification to avoid an extra redirect
    return vote()

    flash("Incorrect OTP.", "danger")
    return redirect(url_for('index'))

@app.route('/vote')
def vote():
    if 'voter_id' not in session:
        return redirect(url_for('index'))

    if not is_election_open():
        # Show the election closed page when voting is not open
        return render_template('voter/election_closed.html')

    voter_id = session['voter_id']

    conn = db_connection()
    has_voted = conn.execute("SELECT has_voted FROM voters WHERE voter_id=?", (voter_id,)).fetchone()[0]
    if has_voted:
        conn.close()
        flash("You have already voted.", "info")
        return redirect(url_for('thank_you'))

    active = conn.execute("SELECT id FROM elections WHERE is_active=1 LIMIT 1").fetchone()
    if active:
        candidates = conn.execute("SELECT * FROM candidates WHERE election_id=?", (active['id'],)).fetchall()
    else:
        candidates = []
    conn.close()

    return render_template('voter/vote.html', candidates=candidates)

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if 'voter_id' not in session:
        flash("Session expired.", "warning")
        return redirect(url_for('index'))

    if not is_election_open():
        flash("Voting closed.", "danger")
        return redirect(url_for('thank_you'))

    voter_id = session['voter_id']
    candidate_id = request.form.get('candidate')

    conn = db_connection()
    try:
        conn.execute("UPDATE candidates SET votes=votes+1 WHERE candidate_id=?", (candidate_id,))
        conn.execute("UPDATE voters SET has_voted=1 WHERE voter_id=?", (voter_id,))
        conn.execute("INSERT INTO logs (action, user_id, ip_address) VALUES (?, ?, ?)",
                     ("vote_cast", voter_id, request.remote_addr))
        conn.commit()
    finally:
        conn.close()

    session.pop('voter_id')
    flash("Vote recorded!", "success")
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('voter/thank_you.html')

@app.route('/results')
def results():
    conn = db_connection()
    candidates = conn.execute("SELECT * FROM candidates").fetchall()
    conn.close()
    return render_template('voter/result.html', candidates=candidates)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Run App
if __name__ == '__main__':
    app.run(debug=True, port=5003)
