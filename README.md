# E-Chunav – Secure E-Voting System (SDG 16)

E-Chunav is a secure, transparent, and user-friendly electronic voting system designed to modernize institutional elections.  
The project aligns with the **United Nations Sustainable Development Goal 16 (Peace, Justice, and Strong Institutions)** by promoting fairness, transparency, accountability, and trust in the electoral process.

---

## Key Features

### 🔐 Security & Integrity
- OTP-based voter authentication via email  
- One-person–one-vote enforcement  
- Device/IP-based vote restriction  
- Secure password hashing  
- Detailed audit logs for traceability  

### 🗳️ Voting Experience
- Simple and intuitive voter interface  
- Time-bound voting window with countdown timer  
- Candidate photo and symbol display  
- Instant vote confirmation  

### 📊 Administration & Transparency
- Dedicated admin panel for election control  
- Ability to start, close, and reset elections  
- Candidate and voter management  
- Live vote counting dashboard  
- Real-time result visualization using Chart.js  

### 🌐 Public Access
- Public live vote counting page  
- Real-time turnout and statistics  
- Transparent and tamper-resistant result display  

---

## Technology Stack
- **Backend:** Python (Flask)  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Charts & Visualization:** Chart.js  
- **Database:** SQLite3  
- **Authentication:** OTP verification and session management  

---

## Project Structure

Echunav/
│
├── admin_app.py # Admin panel (election & candidate management)
├── voter_app.py # Voter login, OTP verification, vote casting
├── public_app.py # Public live vote counting
├── init_db.py # Database initialization script
├── config.py # Application configuration
├── database.db # SQLite database
│
├── templates/ # HTML templates
├── static/ # CSS, JS, images, uploads
├── modules/ # Helper modules
├── logs/ # Application logs
│
├── requirements.txt # Python dependencies
├── run_project.sh # Run helper script
├── view_db.py # Database inspection tool
└── README.md # Project documentation


---

## System Requirements
- Python **3.8 or higher**  
- pip (Python package manager)  
- SQLite3  

---

## Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/E-Chunav.git
cd E-Chunav

2️⃣ Create and Activate Virtual Environment
python -m venv venv
source venv/bin/activate     # Linux / macOS
venv\Scripts\activate        # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Initialize the Database
python init_db.py


This will:

Create all required database tables

Insert default admin credentials

Initialize the first election

5️⃣ Run the Applications

Open three separate terminals (or run individually):

python admin_app.py     # Admin Panel → http://127.0.0.1:5004
python voter_app.py     # Voter Panel → http://127.0.0.1:5000
python public_app.py    # Live Count → http://127.0.0.1:5001

Usage Guide
👤 Voter Flow

Enter Voter ID

Receive OTP via registered email

Verify OTP

Cast vote within the allowed time

Receive vote confirmation

🛠️ Admin Flow

Login at /admin

Add candidates and voters

Open or close elections

Monitor activity logs

View and export results

Start a new election when required

🌍 Public View

Access live vote counting page

Monitor turnout and results in real time

Security Highlights

OTP-based voter authentication

Secure session handling

Password hashing using Werkzeug

SQL injection prevention

Role-based access (Admin vs Voter)

Complete audit logging

UN SDG Alignment

This project contributes to SDG 16 by:

Strengthening institutional decision-making

Ensuring transparent and fair elections

Promoting trust through auditability and openness

Future Enhancements

Blockchain-based vote storage

Facial or biometric verification

Multi-election analytics dashboard

Cloud deployment

Mobile application support

License

This project is developed for academic and educational purposes.


---

If you want, I can also:
- Add **screenshots section**
- Create a **Deployment / Hosting guide**
- Add **default admin credentials note**
- Make a **short README for submissions**

Just tell me 👍
