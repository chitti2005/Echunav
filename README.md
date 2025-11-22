# E-Voting System

A secure and user-friendly electronic voting system built with Flask.

## Features

- Secure voter authentication with OTP verification
- 20-second voting timer to prevent delays
- Admin panel for candidate management
- Real-time voting statistics
- Result visualization using Chart.js
- Mobile-responsive design

## Requirements

- Python 3.8+
- Flask
- SQLite3
- Additional requirements in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/e_voting_system.git
cd e_voting_system
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python init_db.py
```

5. Start the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

### Voter Flow:
1. Enter Voter ID and phone number
2. Receive and enter OTP
3. Cast vote within 20 seconds
4. Receive confirmation

### Admin Flow:
1. Access admin panel at `/admin`
2. Login with admin credentials
3. Manage candidates and view statistics

## Security Features

- OTP-based voter authentication
- Session management
- SQL injection prevention
- CSRF protection
- Secure password handling

## Directory Structure

```
e_voting_system/
│
├── app.py                     # Main Flask application
├── config.py                  # Configuration settings
├── init_db.py                # Database initialization
├── database.db               # SQLite database
│
├── static/                   # Static assets
├── templates/                # HTML templates
├── modules/                  # Python modules
└── logs/                    # Application logs
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask framework
- Bootstrap for UI
- Chart.js for visualizations