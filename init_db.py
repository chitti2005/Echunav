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
        
        cur.execute("""
    CREATE TABLE IF NOT EXISTS elections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        is_active INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
   """)
    # ===========================================
    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
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
   
    cur.execute("""
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        voter_id TEXT UNIQUE,
        name TEXT,
        email TEXT,
        password_hash TEXT,
        has_voted INTEGER DEFAULT 0
    )
""")

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
    


    # ===========================================
    # SAMPLE VOTERS (your team)
    # ===========================================
    
    voters = [
    ('v3004', 'ABHINAV K', 'abhinav.is23@sahyadri.edu.in', generate_password_hash('abh123')),
    ('v3005', 'ABHISHEK ADIGA', 'abhishek.is23@sahyadri.edu.in', generate_password_hash('abh1123')),
    ('v3006', 'ABHISHEK L R', 'abhishekl.is23@sahyadri.edu.in', generate_password_hash('abh2123')),
    ('v3008', 'ADITHI SHETTY', 'adithi.is23@sahyadri.edu.in', generate_password_hash('adi123')),
    ('v3009', 'ADITHYA K S', 'adithya.cs23@sahyadri.edu.in', generate_password_hash('adi1123')),
    ('v3010', 'ADITYA M NAIK', 'aditya.is23@sahyadri.edu.in', generate_password_hash('adi2123')),
    ('v3013', 'AMAN A K', 'aman.is23@sahyadri.edu.in', generate_password_hash('ama123')),
    ('v3015', 'AMRUTH M S', 'amruth.is23@sahyadri.edu.in', generate_password_hash('amr123')),
    ('v3016', 'ANANYA', 'ananya.is23@sahyadri.edu.in', generate_password_hash('ana123')),
    ('v3019', 'ANVITH', 'anvith.is23@sahyadri.edu.in', generate_password_hash('anv123')),
    ('v3021', 'ARJUN R DEVADIGA', 'arjunr.is23@sahyadri.edu.in', generate_password_hash('arj123')),
    ('v3025', 'ASHMITA ARUN KURDEKAR', 'ashmita.is23@sahyadri.edu.in', generate_password_hash('ash123')),
    ('v3028', 'BEN LEON DSOUZA', 'ben.is23@sahyadri.edu.in', generate_password_hash('ben123')),
    ('v3030', 'BHAVISH K PADMASHALI', 'bhavish.is23@sahyadri.edu.in', generate_password_hash('bha123')),
    ('v3032', 'CHAITHRA B H', 'chaithra.is23@sahyadri.edu.in', generate_password_hash('cha123')),
    ('v3033', 'CHETAN S BALIGA', 'chetan.is23@sahyadri.edu.in', generate_password_hash('che123')),
    ('v3035', 'CHITTESH S K', 'chittesh.is23@sahyadri.edu.in', generate_password_hash('chi123')),
    ('v3038', 'DISHA', 'disha.is23@sahyadri.edu.in', generate_password_hash('dis123')),
    ('v3040', 'DIVAN D SHETTY', 'divan.is23@sahyadri.edu.in', generate_password_hash('div123')),
    ('v3041', 'DIVYA K', 'divya.is23@sahyadri.edu.in', generate_password_hash('div1123')),
    ('v3043', 'FATHIMA SHAZNEEN', 'fathima.is23@sahyadri.edu.in', generate_password_hash('fat123')),
    ('v3044', 'H SANGINI KEDILAYA', 'sangini.is23@sahyadri.edu.in', generate_password_hash('san123')),
    ('v3045', 'HARSHAN R ARASA', 'harshan.is23@sahyadri.edu.in', generate_password_hash('har123')),
    ('v3049', 'JAYADITHYA G SALIAN', 'jayadithya.is23@sahyadri.edu.in', generate_password_hash('jay123')),
    ('v3051', 'KARTIK MANJUNATH RAIKAR', 'kartik.is23@sahyadri.edu.in', generate_password_hash('kar123')),
    ('v3052', 'KAVYA R', 'kavyar.is23@sahyadri.edu.in', generate_password_hash('kav123')),
    ('v3054', 'KUSHITHA', 'kushitha.is23@sahyadri.edu.in', generate_password_hash('kus123')),
    ('v3056', 'MEGHNA SURESH', 'meghna.is23@sahyadri.edu.in', generate_password_hash('meg123')),
    ('v3058', 'MOHAMMED AIZ', 'aiz.is23@sahyadri.edu.in', generate_password_hash('moh123')),
    ('v3059', 'MUKASSHAF AHMED', 'mukasshaf.is23@sahyadri.edu.in', generate_password_hash('muk123')),
    ('v3061', 'NIDHI K', 'nidhik.is23@sahyadri.edu.in', generate_password_hash('nid123')),
    ('v3064', 'NISHANTH SHETTY', 'nishanth.is23@sahyadri.edu.in', generate_password_hash('nis123')),
    ('v3069', 'PRANITH M KUNDAR', 'pranith.is23@sahyadri.edu.in', generate_password_hash('pra123')),
    ('v3071', 'PRATHVI SHIVANAND NAIK', 'prathvi.is23@sahyadri.edu.in', generate_password_hash('pra1123')),
    ('v3077', 'RAKSHITHA N', 'rakshita.is23@sahyadri.edu.in', generate_password_hash('rak123')),
    ('v3079', 'RASHAD DAWOOD YUSUF', 'rashad.is23@sahyadri.edu.in', generate_password_hash('ras123')),
    ('v3080', 'RASHMITHA B', 'rashmitha.is23@sahyadri.edu.in', generate_password_hash('ras1123')),
    ('v3086', 'SAMRUDH S RAI', 'samrudh.is23@sahyadri.edu.in', generate_password_hash('sam123')),
    ('v3087', 'SAMSKRUTI JOSHI', 'samskruti.is23@sahyadri.edu.in', generate_password_hash('sam1123')),
    ('v3088', 'SANIYA', 'saniya.is23@sahyadri.edu.in', generate_password_hash('san1123')),
    ('v3091', 'SANNIDHI', 'sannidhi.is23@sahyadri.edu.in', generate_password_hash('san2123')),
    ('v3092', 'SHASHWATH B KARKERA', 'shashwath.is23@sahyadri.edu.in', generate_password_hash('sha123')),
    ('v3095', 'SHRAVYA', 'shravya.is23@sahyadri.edu.in', generate_password_hash('shr123')),
    ('v3097', 'SHRUTHI', 'shruthi.is23@sahyadri.edu.in', generate_password_hash('shr1123')),
    ('v3099', 'SOUMYA R', 'soumya.is23@sahyadri.edu.in', generate_password_hash('sou123')),
    ('v3100', 'SRUJAN', 'srujan.is23@sahyadri.edu.in', generate_password_hash('sru123')),
    ('v3103', 'SUJAN P', 'sujan.is23@sahyadri.edu.in', generate_password_hash('suj123')),
    ('v3104', 'SUJEETH Y S', 'sujeeth.is23@sahyadri.edu.in', generate_password_hash('suj1123')),
    ('v3105', 'SUJITH S BANGERA', 'sujith.is23@sahyadri.edu.in', generate_password_hash('suj2123')),
    ('v3113', 'V SHREYAS SHANKAR', 'shreyas.is23@sahyadri.edu.in', generate_password_hash('vsh123')),
    ('v3114', 'VAISHNAV S', 'vaishnav.is23@sahyadri.edu.in', generate_password_hash('vai123')),
    ('v3115', 'VARNITA M N', 'varnita.is23@sahyadri.edu.in', generate_password_hash('var123')),
    ('v3116', 'VARSHA', 'varsha.is23@sahyadri.edu.in', generate_password_hash('var1123')),
    ('v3117', 'VARSHA K', 'varshak.is23@sahyadri.edu.in', generate_password_hash('var2123')),
    ('v3119', 'VIJAYALAKSHMI KANNAN', 'vijayalakshmi.is23@sahyadri.edu.in', generate_password_hash('vij123')),
    ('v3120', 'VIJETH KUMAR', 'vijeth.is23@sahyadri.edu.in', generate_password_hash('vij1123')),
    ('v3122', 'VIKAS H NAIK', 'vikas.is23@sahyadri.edu.in', generate_password_hash('vik123')),
    ('v3123', 'Y G PAVAN', 'pavan.is23@sahyadri.edu.in', generate_password_hash('pav123')),
    ('v3124', 'YASH', 'yash.is23@sahyadri.edu.in', generate_password_hash('yas123')),
    ('v3125', 'YASH UDAY VERNEKAR', 'yashuday.is23@sahyadri.edu.in', generate_password_hash('yas1123')),
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
