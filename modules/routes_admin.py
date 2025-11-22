from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import sqlite3
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin123':  # Use config in production
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid credentials', 'error')
    
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Get candidates
    c.execute('SELECT id, name, party, image_path FROM candidates')
    candidates = [dict(zip(['id', 'name', 'party', 'image_path'], row)) for row in c.fetchall()]
    
    # Get statistics
    c.execute('SELECT COUNT(*) FROM voters')
    total_voters = c.fetchone()[0]
    
    c.execute('SELECT COUNT(*) FROM voters WHERE has_voted = 1')
    votes_cast = c.fetchone()[0]
    
    conn.close()
    
    stats = {
        'total_voters': total_voters,
        'votes_cast': votes_cast,
        'remaining_voters': total_voters - votes_cast
    }
    
    return render_template('admin_dashboard.html', candidates=candidates, stats=stats)

@admin_bp.route('/candidate/add', methods=['GET', 'POST'])
@admin_required
def add_candidate():
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        image = request.files.get('image')
        
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join('images/candidates', filename)
            image.save(os.path.join('static', image_path))
        else:
            image_path = None
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO candidates (name, party, image_path) VALUES (?, ?, ?)',
                 (name, party, image_path))
        conn.commit()
        conn.close()
        
        flash('Candidate added successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('add_candidate.html')

@admin_bp.route('/candidate/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_candidate(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name')
        party = request.form.get('party')
        image = request.files.get('image')
        
        if image:
            filename = secure_filename(image.filename)
            image_path = os.path.join('images/candidates', filename)
            image.save(os.path.join('static', image_path))
            
            c.execute('UPDATE candidates SET name=?, party=?, image_path=? WHERE id=?',
                     (name, party, image_path, id))
        else:
            c.execute('UPDATE candidates SET name=?, party=? WHERE id=?',
                     (name, party, id))
        
        conn.commit()
        flash('Candidate updated successfully', 'success')
        return redirect(url_for('admin.dashboard'))
    
    c.execute('SELECT id, name, party, image_path FROM candidates WHERE id=?', (id,))
    candidate = dict(zip(['id', 'name', 'party', 'image_path'], c.fetchone()))
    conn.close()
    
    return render_template('add_candidate.html', candidate=candidate)

@admin_bp.route('/candidate/<int:id>/delete', methods=['POST'])
@admin_required
def delete_candidate(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Get image path before deletion
    c.execute('SELECT image_path FROM candidates WHERE id=?', (id,))
    result = c.fetchone()
    if result and result[0]:
        image_path = os.path.join('static', result[0])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    c.execute('DELETE FROM candidates WHERE id=?', (id,))
    conn.commit()
    conn.close()
    
    flash('Candidate deleted successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))