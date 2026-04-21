# AI Expense Tracker v2 — Full Stack (Flask + CSV)

## Run in 2 steps
```bash
pip install flask werkzeug
python app.py
```
Open → http://localhost:5000

## Project Structure
```
expense_tracker_v2/
├── app.py                     ← Flask backend (API + CSV logic)
├── requirements.txt           ← Python deps
├── templates/
│   └── index.html             ← Full frontend (Login + App)
└── data/                      ← AUTO-CREATED on first run
    ├── users.csv              ← All registered users
    └── expenses_<ID>.csv      ← One expense file per user
```

## CSV Data Format

### data/users.csv
| user_id | username | name | email | contact | password_hash | created_at |
|---------|----------|------|-------|---------|---------------|------------|
| 0ADE3550 | rahul_s | Rahul Sharma | rahul@test.com | 9876543210 | sha256... | 2026-04-11T... |

### data/expenses_<user_id>.csv
| expense_id | user_id | amount | category | description | date | source |
|------------|---------|--------|----------|-------------|------|--------|
| abc123 | 0ADE3550 | 249.0 | Food | Swiggy Biryani | 2026-04-11T... | text |

## Login Options
Users can log in with any ONE of:
- Username + Password
- Email Address + Password
- Contact Number + Password

Wrong password or unknown identifier → blocked with clear error.

## Features
- Split login/register page with dark-gold editorial design
- AI NLP: extracts amount via regex, category via keyword dictionary
- Voice input (Web Speech API — Chrome/Edge)
- Screenshot OCR (simulated; plug in Tesseract.js for real OCR)
- Dashboard: 3 live charts (Pie, Line, Bar)
- Reports: Monthly chart + Doughnut + AI Insights
- CSV export per user with category summary
- Per-user isolated expense data
