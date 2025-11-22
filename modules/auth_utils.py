import random
import string
import sqlite3
from datetime import datetime, timedelta

def generate_otp(voter_id, length=6):
    """Generate OTP and store in database"""
    otp = ''.join(random.choices(string.digits, k=length))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Remove any existing OTP for this voter
    c.execute('DELETE FROM otp WHERE voter_id = ?', (voter_id,))
    
    # Store new OTP
    c.execute('INSERT INTO otp (voter_id, otp) VALUES (?, ?)', (voter_id, otp))
    conn.commit()
    conn.close()
    
    return otp

def verify_otp_value(voter_id, otp):
    """Verify OTP value and expiry"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Get OTP record
    c.execute('''SELECT otp, created_at FROM otp 
                 WHERE voter_id = ? 
                 ORDER BY created_at DESC LIMIT 1''', (voter_id,))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False
    
    stored_otp, created_at = result
    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
    
    # Check if OTP is expired (5 minutes validity)
    if datetime.now() - created_at > timedelta(minutes=5):
        conn.close()
        return False
    
    # Verify OTP value
    is_valid = stored_otp == otp
    
    if is_valid:
        # Remove used OTP
        c.execute('DELETE FROM otp WHERE voter_id = ?', (voter_id,))
        conn.commit()
    
    conn.close()
    return is_valid

def authenticate_voter(voter_id, phone):
    """Check if voter exists with given credentials"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''SELECT 1 FROM voters 
                 WHERE voter_id = ? AND phone_number = ? 
                 AND has_voted = 0''', (voter_id, phone))
    result = c.fetchone() is not None
    
    conn.close()
    return result