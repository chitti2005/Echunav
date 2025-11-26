# admin_app.py
import os
import time
import random
import string
import sqlite3
import smtplib
import re

from email.mime.text import MIMEText
from fpdf import FPDF

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------------------------
# Config
# ---------------------------
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'super_secret_admin_key')

DB_PATH = 'database.db'  # same DB as voter_app
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXT

def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def send_email(to_email, subject, body):
    sender = os.environ.get('SMTP_SENDER')
    pwd = os.environ.get('SMTP_PASSWORD')
    if not (sender and pwd):
        # dev fallback: log to console
        print("Email (dev) ->", to_email, subject, body)
        return False
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to_email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, pwd)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("send_email error:", e)
        return False

def ensure_election_status_row():
    conn = db_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO election_status (id, status) VALUES (1, 'OPEN')")
        conn.commit()
    except Exception as e:
        print("ensure_election_status_row error:", e)
    finally:
        conn.close()

ensure_election_status_row()

# ---------------------------
# Admin routes
# ---------------------------

# show login page (both /admin and /admin/login accepted)
@app.route('/admin', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        conn = db_connection()
        admin = conn.execute("SELECT * FROM admin WHERE username=?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin'] = username
            flash("Welcome, admin.", "success")
            return redirect(url_for('admin_dashboard'))
        flash("Invalid credentials.", "danger")
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        flash("Please log in as admin.", "warning")
        return redirect(url_for('admin_login'))

    conn = db_connection()
    try:
        active = conn.execute("SELECT id FROM elections WHERE is_active=1 LIMIT 1").fetchone()
        if active:
            candidates = conn.execute("SELECT * FROM candidates WHERE election_id=?", (active['id'],)).fetchall()
        else:
            candidates = conn.execute("SELECT * FROM candidates").fetchall()

        logs = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 20").fetchall()
        total_voters = conn.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
        total_votes = conn.execute("SELECT COUNT(*) FROM voters WHERE has_voted=1").fetchone()[0]
        participation = round((total_votes / total_voters * 100), 2) if total_voters else 0

        status_row = conn.execute("SELECT status FROM election_status WHERE id=1").fetchone()
        election_open = (status_row['status'] == 'OPEN') if status_row else False

    except Exception as e:
        print("admin_dashboard error:", e)
        candidates, logs, total_voters, total_votes, participation, election_open = [], [], 0, 0, 0, False
    finally:
        conn.close()

    return render_template('admin/dashboard.html',
                           candidates=candidates,
                           logs=logs,
                           total_voters=total_voters,
                           total_votes=total_votes,
                           participation=participation,
                           election_open=election_open)

# Add candidate (via form on dashboard or add_candidate page)
@app.route('/admin/add_candidate', methods=['POST', 'GET'])
def admin_add_candidate():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'GET':
        # optional: render add_candidate form if you want a separate page
        return render_template('admin/add_candidate.html', candidate=None)

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    photo_file = request.files.get('photo') or request.files.get('image')  # support both input names
    symbol_file = request.files.get('symbol')

    photo_filename = None
    symbol_filename = None

    try:
        if photo_file and photo_file.filename and allowed_file(photo_file.filename):
            # Check file size manually (less than 2 MB)
            try:
                file_obj = getattr(photo_file, 'stream', photo_file)
                file_obj.seek(0, os.SEEK_END)
                photo_size = file_obj.tell()
                file_obj.seek(0)
            except Exception:
                photo_size = None

            if photo_size and photo_size > 2 * 1024 * 1024:
                flash("Photo is too large! Maximum size is 2 MB.", "danger")
                return redirect(url_for('admin_dashboard'))

            fname = secure_filename(photo_file.filename)
            unique = f"{int(time.time())}_{random.randint(1000,9999)}_{fname}"
            photo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique))
            photo_filename = os.path.join('uploads', unique)  # store relative path for url_for

        if symbol_file and symbol_file.filename and allowed_file(symbol_file.filename):
            sname = secure_filename(symbol_file.filename)
            unique_s = f"{int(time.time())}_{random.randint(1000,9999)}_{sname}"
            symbol_file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_s))
            symbol_filename = os.path.join('uploads', unique_s)
    except Exception as e:
        print("file save error:", e)
        flash("Failed to save uploaded files.", "warning")

    conn = db_connection()
    try:
        active = conn.execute("SELECT id FROM elections WHERE is_active=1 LIMIT 1").fetchone()
        if active:
            conn.execute("INSERT INTO candidates (election_id, name, description, photo, symbol, votes) VALUES (?, ?, ?, ?, ?, 0)",
                         (active['id'], name, description, photo_filename, symbol_filename))
        else:
            conn.execute("INSERT INTO candidates (name, description, photo, symbol, votes) VALUES (?, ?, ?, ?, 0)",
                         (name, description, photo_filename, symbol_filename))
        conn.commit()
        flash("Candidate added successfully.", "success")
    except Exception as e:
        conn.rollback()
        print("add_candidate db error:", e)
        flash("Failed to add candidate.", "danger")
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

# Add voter
@app.route('/admin/add_voter', methods=['POST'])
def admin_add_voter():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    voter_id = request.form.get('voter_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()

    if not voter_id or not name or not email:
        flash("All fields required.", "warning")
        return redirect(url_for('admin_dashboard'))

    if not valid_email(email):
        flash("Enter a valid email address.", "warning")
        return redirect(url_for('admin_dashboard'))

    conn = db_connection()
    try:
        exists = conn.execute("SELECT 1 FROM voters WHERE voter_id=? OR email=?", (voter_id, email)).fetchone()
        if exists:
            flash("Voter ID or email already exists.", "danger")
            return redirect(url_for('admin_dashboard'))

        temp_pw = generate_password()
        pw_hash = generate_password_hash(temp_pw)
        conn.execute("INSERT INTO voters (voter_id, name, email, password_hash, has_voted) VALUES (?, ?, ?, ?, 0)",
                     (voter_id, name, email, pw_hash))
        conn.commit()

        # try to email the temporary password (best-effort)
        subject = "E-Chunav: Voter Registration"
        body = f"You have been registered for E-Chunav.\nVoter ID: {voter_id}\nTemporary password: {temp_pw}\nPlease login and change your password."
        sent = send_email(email, subject, body)
        if sent:
            flash("Voter added and email sent with temporary password.", "success")
        else:
            flash(f"Voter added. Temporary password: {temp_pw}", "success")
    except Exception as e:
        conn.rollback()
        print("admin_add_voter error:", e)
        flash("Failed to add voter.", "danger")
    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

# Toggle election (open/close)
@app.route('/admin/toggle_election', methods=['POST'])
def admin_toggle_election():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = db_connection()
    try:
        row = conn.execute("SELECT status FROM election_status WHERE id=1").fetchone()
        if row and row['status'] == 'OPEN':
            conn.execute("UPDATE election_status SET status='CLOSED' WHERE id=1")
        else:
            conn.execute("UPDATE election_status SET status='OPEN' WHERE id=1")
        conn.commit()
        flash("Election status toggled.", "info")
    except Exception as e:
        conn.rollback()
        print("toggle_election error:", e)
        flash("Failed to toggle election status.", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

# Explicit set status (OPEN/CLOSED)
@app.route('/admin/set_status', methods=['POST'])
def admin_set_status():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    new_status = request.form.get('status', '').upper()
    if new_status not in ('OPEN', 'CLOSED'):
        flash("Invalid status.", "warning")
        return redirect(url_for('admin_dashboard'))
    conn = db_connection()
    try:
        conn.execute("INSERT OR REPLACE INTO election_status (id, status) VALUES (1, ?)", (new_status,))
        conn.commit()
        flash(f"Election status set to {new_status}.", "success")
    except Exception as e:
        conn.rollback()
        print("set_status error:", e)
        flash("Failed to set status.", "danger")
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

# OTP logs viewer
@app.route('/admin/otp-logs')
@app.route('/admin/otp_logs')
def admin_otp_logs():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = db_connection()
    logs = conn.execute("""
        SELECT otp_log.*, voters.name
        FROM otp_log
        LEFT JOIN voters ON otp_log.voter_id = voters.voter_id
        ORDER BY timestamp DESC LIMIT 200
    """).fetchall()
    conn.close()
    return render_template('admin/otp_logs.html', logs=logs)

# Download DB
@app.route('/admin/download_db')
def admin_download_db():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    if not os.path.exists(DB_PATH):
        flash("Database not found.", "danger")
        return redirect(url_for('admin_dashboard'))
    return send_file(DB_PATH, as_attachment=True)

# Download results PDF
@app.route('/admin/download_results')
def admin_download_results():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = db_connection()
    candidates = conn.execute("SELECT * FROM candidates").fetchall()
    total_votes = conn.execute("SELECT COUNT(*) FROM voters WHERE has_voted=1").fetchone()[0]
    total_voters = conn.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
    conn.close()

    participation = round((total_votes / total_voters * 100), 2) if total_voters else 0

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Election Results", ln=True, align='C')
    pdf.ln(6)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Total Voters: {total_voters}", ln=True)
    pdf.cell(0, 8, f"Votes Cast: {total_votes}", ln=True)
    pdf.cell(0, 8, f"Participation: {participation}%", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(120, 8, "Candidate", border=1)
    pdf.cell(40, 8, "Votes", border=1, ln=True)

    pdf.set_font("Arial", size=12)
    for c in candidates:
        pdf.cell(120, 8, str(c['name']), border=1)
        pdf.cell(40, 8, str(c['votes']), border=1, ln=True)

    filename = "Election_Results.pdf"
    pdf.output(filename)
    return send_file(filename, as_attachment=True)

# Results page (admin can also view)
@app.route('/admin/results')
def admin_results():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    conn = db_connection()
    try:
        active = conn.execute("SELECT id FROM elections WHERE is_active=1 LIMIT 1").fetchone()
        if active:
            candidates = conn.execute("SELECT * FROM candidates WHERE election_id=?", (active['id'],)).fetchall()
        else:
            candidates = conn.execute("SELECT * FROM candidates").fetchall()
    except Exception as e:
        print("admin_results error:", e)
        candidates = []
    finally:
        conn.close()
    return render_template('admin/results.html', candidates=candidates)

# Admin logout (separate to avoid interfering with voter logout)
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash("Admin logged out.", "info")
    return redirect(url_for('admin_login'))

# Suspicious IPs analysis

@app.route('/admin/suspicious_ips')
def suspicious_ips():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = db_connection()
    data = conn.execute("""
        SELECT 
            ip_address,
            SUM(CASE WHEN action='login' THEN 1 ELSE 0 END) AS login_count,
            SUM(CASE WHEN action='vote_cast' THEN 1 ELSE 0 END) AS vote_count,
            COUNT(DISTINCT user_id) AS unique_voters
        FROM logs
        WHERE ip_address IS NOT NULL AND ip_address != ''
        GROUP BY ip_address
        ORDER BY vote_count DESC, login_count DESC
    """).fetchall()
    conn.close()

    # Prepare analysis for template
    ip_analysis = []
    for row in data:
        risk = "Low"
        if row['vote_count'] >= 2:
            risk = "High"
        elif row['unique_voters'] >= 3:
            risk = "Medium"
        elif row['login_count'] >= 10:
            risk = "Medium"

        ip_analysis.append({
            "ip": row["ip_address"],
            "logins": row["login_count"],
            "votes": row["vote_count"],
            "users": row["unique_voters"],
            "risk": risk
        })

    return render_template("admin/suspicious_ips.html", ips=ip_analysis)


# New election (reset votes, create new election entry)

from datetime import datetime

# Add near the other admin routes

@app.route('/admin/new_election', methods=['POST'])
def admin_new_election():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = db_connection()
    cur = conn.cursor()

    try:
        # 🔥 1. Close all existing elections
        cur.execute("UPDATE elections SET is_active = 0")

        # 🔥 2. Create NEW election
        cur.execute("""
            INSERT INTO elections (name, description, is_active)
            VALUES ('New Election', 'Reset and started fresh', 1)
        """)
        new_election_id = cur.lastrowid

        # 🔥 3. Clear ALL candidates
        cur.execute("DELETE FROM candidates")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='candidates'")

        # 🔥 4. Reset voter status
        cur.execute("UPDATE voters SET has_voted = 0")

        # 🔥 5. CLEAR ALL LOGS
        cur.execute("DELETE FROM logs")
        cur.execute("DELETE FROM otp_log")

        # Reset AUTO INCREMENT counters
        cur.execute("DELETE FROM sqlite_sequence WHERE name='logs'")
        cur.execute("DELETE FROM sqlite_sequence WHERE name='otp_log'")

        # 🔥 6. Update election status table
        cur.execute("UPDATE election_status SET status='OPEN' WHERE id=1")

        conn.commit()
        flash("✅ New election started successfully!", "success")

    except Exception as e:
        conn.rollback()
        print("new_election error:", e)
        flash("⚠ Failed to start new election.", "danger")

    finally:
        conn.close()

    return redirect(url_for('admin_dashboard'))

    # verify admin password from DB
    conn = db_connection()
    try:
        admin_row = conn.execute("SELECT password_hash FROM admin WHERE username=?", (session['admin'],)).fetchone()
        if not admin_row or not check_password_hash(admin_row['password_hash'], entered_pw):
            flash("Incorrect admin password. New election cancelled.", "danger")
            return redirect(url_for('admin_login'))

        # Start transaction
        cur = conn.cursor()

        # Find current active election id (if any)
        cur.execute("SELECT id FROM elections WHERE is_active=1 ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        old_election_id = row['id'] if row else None

        # SOFT MODE (recommended): mark all existing elections inactive, create new active election
        if mode == 'soft':
            # deactivate previous elections
            cur.execute("UPDATE elections SET is_active=0 WHERE is_active=1")
            # create new election row (optionally add name)
            now = datetime.utcnow().isoformat(sep=' ', timespec='seconds')
            cur.execute("INSERT INTO elections (name, is_active, created_at) VALUES (?, 1, ?)",
                        (f"Election {now}", now))
            new_election_id = cur.lastrowid

            # Important: do NOT modify existing candidate rows. New election begins empty.

            # Optionally reset voters' has_voted flag so they can vote in the new election.
            # If you want per-election voter tracking, consider adding a votes_per_election table instead.
            cur.execute("UPDATE voters SET has_voted = 0")

            conn.commit()
            flash("New election created (soft). Previous election archived (inactive).", "success")
            return redirect(url_for('admin_login'))

        # HARD MODE: archive candidates / reset votes (destructive)
        elif mode == 'hard':
            # ensure archive table exists (create-safe)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS candidates_archive (
                  archive_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_candidate_id INTEGER,
                  election_id INTEGER,
                  name TEXT,
                  description TEXT,
                  photo TEXT,
                  symbol TEXT,
                  votes INTEGER,
                  archived_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # archive current candidates (if old election exists)
            if old_election_id:
                cur.execute("""
                    INSERT INTO candidates_archive
                       (original_candidate_id, election_id, name, description, photo, symbol, votes, archived_at)
                    SELECT candidate_id, election_id, name, description, photo, symbol, votes, CURRENT_TIMESTAMP
                    FROM candidates WHERE election_id=?
                """, (old_election_id,))

            # deactivate previous elections
            cur.execute("UPDATE elections SET is_active=0 WHERE is_active=1")

            # create NEW election row
            now = datetime.utcnow().isoformat(sep=' ', timespec='seconds')
            cur.execute("INSERT INTO elections (name, is_active, created_at) VALUES (?, 1, ?)",
                        (f"Election {now}", now))
            new_election_id = cur.lastrowid

            # Reset candidate votes for new election (we keep candidate rows separate; better to insert fresh candidates)
            # If you had previously reused candidate rows, reset their votes to 0 but keep them unlinked to new election.
            cur.execute("UPDATE candidates SET votes = 0 WHERE election_id IS NULL OR election_id = ?", (new_election_id,))

            # Reset all voters so they can vote again
            cur.execute("UPDATE voters SET has_voted = 0")

            # Optionally clear logs and OTP logs (destructive)
            cur.execute("DELETE FROM logs")
            cur.execute("DELETE FROM otp_log")

            conn.commit()
            flash("New election created (hard). Old data archived and logs cleared.", "warning")
            return redirect(url_for('admin_login'))

        else:
            flash("Unknown mode for new_election. Use mode=soft or mode=hard.", "danger")
            return redirect(url_for('admin_login'))

    except Exception as e:
        conn.rollback()
        print("admin_new_election error:", e)
        flash("Failed to create new election (see server logs).", "danger")
        return redirect(url_for('admin_login'))
    finally:
        conn.close()


        

    

# ---------------------------
# Error handlers
# ---------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ---------------------------
# Run app
# ---------------------------
if __name__ == '__main__':
    # Use port 5001 for admin app (voter app runs on 5000)
    app.run(host='127.0.0.1', port=5006, debug=True)
