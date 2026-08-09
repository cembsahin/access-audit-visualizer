# Access Review & Audit Log Visualizer

![Tests](https://github.com/cembsahin/access-audit-visualizer/actions/workflows/tests.yml/badge.svg)

A full-stack web app that ingests identity/access export CSVs (Okta-style) and flags stale or high-risk accounts, visualizing access patterns by department.

Built after doing this kind of access review manually as part of IT/identity administration work — this is a generalized, public version of that workflow.

## Features

- **CSV upload** of identity/access data (username, department, role, status, last login)
- **Automatic risk flagging**: accounts inactive 90+ days are marked stale; stale accounts with admin-level roles are flagged high risk
- **Dashboard** with:
  - Access-by-department bar chart
  - Active vs. stale doughnut chart
  - Full account detail table with color-coded risk rows
- Sample dataset included so you can try it immediately

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy, pandas
- **Database:** SQLite
- **Frontend:** Jinja2 templates, Chart.js
- **Data processing:** pandas for CSV parsing and risk-flag computation

## Running locally

```bash
git clone https://github.com/cembsahin/access-audit-visualizer.git
cd access-audit-visualizer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`, upload `sample_data/sample_access_log.csv`, and view the dashboard.

## CSV format

| Column | Description |
|---|---|
| `username` | Account identifier |
| `department` | Department the account belongs to |
| `role` | Job/access role (roles containing "admin" are treated as elevated) |
| `status` | Active / Suspended / etc. |
| `last_login` | Date of last login (`YYYY-MM-DD`) |

## Roadmap

- [ ] CSV export of flagged accounts
- [ ] Configurable stale-account threshold
- [ ] Multi-file historical comparison (trend over time)
- [ ] Deploy live demo

## Why I built this

I spent years administering Okta, Azure AD, and Active Directory, including running access reviews by hand. This project turns that recurring manual process into a small web tool — combining that domain background with the full-stack skills I'm building now.
