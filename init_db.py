import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    print("⚙ Resetting database...")

    # ⚠ Drop ALL tables (safe for development only)
    tables = [
        "voters", "candidates", "admin", "logs", "otp_log",
        "elections", "settings", "election_status"
    ]
    for t in tables:
        cur.execute(f"DROP TABLE IF EXISTS {t}")

    # ===========================================
    # 1️⃣  VOTERS TABLE
    # ===========================================
    cur.execute("""
        CREATE TABLE voters (
            voter_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            has_voted INTEGER DEFAULT 0
        )
    """)

    # ===========================================
    # 2️⃣  ADMIN TABLE
    # ===========================================
    cur.execute("""
        CREATE TABLE admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    # Insert default admin
    cur.execute("""
        INSERT INTO admin (username, password_hash)
        VALUES (?, ?)
    """, ("admin", generate_password_hash("admin123")))

    print("✔ Default admin added (username: admin, password: admin123)")

    # ===========================================
    # 3️⃣  ELECTIONS TABLE
    # ===========================================
    cur.execute("""
        CREATE TABLE elections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert ONE active election (important!)
    cur.execute("""
        INSERT INTO elections (name, description, is_active)
        VALUES ('Default Election', 'Automatically created election', 1)
    """)

    print("✔ Default election created & activated")

    # ===========================================
    # 4️⃣  CANDIDATES TABLE
    # ===========================================
    cur.execute("""
        CREATE TABLE candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            election_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            photo TEXT,
            symbol TEXT,
            votes INTEGER DEFAULT 0,
            FOREIGN KEY (election_id) REFERENCES elections(id)
        )
    """)

    # ===========================================
    # 5️⃣  LOGS TABLE (with IP column)
    # ===========================================
    cur.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            user_id TEXT,
            ip_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ===========================================
    # 6️⃣  OTP LOG TABLE
    # ===========================================
    cur.execute("""
        CREATE TABLE otp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT,
            email TEXT,
            otp TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ===========================================
    # 7️⃣  SETTINGS TABLE (fallback)
    # ===========================================
    cur.execute("""
        CREATE TABLE settings (
            id INTEGER PRIMARY KEY,
            election_open INTEGER DEFAULT 1
        )
    """)

    cur.execute("""
        INSERT INTO settings (id, election_open)
        VALUES (1, 1)
    """)

    # ===========================================
    # 8️⃣  ELECTION STATUS TABLE (explicit OPEN/CLOSED)
    # ===========================================
    cur.execute("""
        CREATE TABLE election_status (
            id INTEGER PRIMARY KEY,
            status TEXT
        )
    """)

    cur.execute("""
        INSERT INTO election_status (id, status)
        VALUES (1, 'OPEN')
    """)

    # ===========================================
    # SAMPLE VOTERS (your team)
    # ===========================================
    voters = [
        ('v101', 'Chetan S Baliga', 'chetan.is23@sahyadri.edu.in', generate_password_hash('che123')),
        ('v102', 'Divya', 'divyanandan025@gmail.com', generate_password_hash('div123')),
        ('v103', 'Shazneen', 'fathima.is23@sahyadri.edu.in', generate_password_hash('sha123')),
        ('v104', 'Ashmita', 'ashmita.is23@sahyadri.edu.in', generate_password_hash('ash123'))
    ]
    cur.executemany("""
        INSERT INTO voters (voter_id, name, email, password_hash)
        VALUES (?, ?, ?, ?)
    """, voters)

    print("✔ Sample voters inserted")

    # Commit & Close
    conn.commit()
    conn.close()

    print("🎉 Database initialized successfully!")


if __name__ == '__main__':
    init_db()
