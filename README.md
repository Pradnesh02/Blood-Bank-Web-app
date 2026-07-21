<div align="center">

<img src="https://img.shields.io/badge/🩸-BloodBank_AI-FF1744?style=for-the-badge&labelColor=121212" alt="BloodBank AI"/>

# BloodBank AI
### Full-Stack Healthcare Intelligence Platform

**Saving Lives, One Drop at a Time.**

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-blood--bank--web--app--5n5c.onrender.com-FF1744?style=for-the-badge&logoColor=white)](https://blood-bank-web-app-5n5c.onrender.com)
[![GitHub Stars](https://img.shields.io/github/stars/Pradnesh02/Blood-Bank-Web-app?style=for-the-badge&color=FF1744&labelColor=121212)](https://github.com/Pradnesh02/Blood-Bank-Web-app/stargazers)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge&labelColor=121212)](LICENSE)

---

![Python](https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask_3.0-000000?style=flat-square&logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![Prophet](https://img.shields.io/badge/Prophet-FF6B35?style=flat-square&logo=meta&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly.js-3F4F75?style=flat-square&logo=plotly&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on_Render-46E3B7?style=flat-square&logo=render&logoColor=white)

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Screenshots](#-screenshots)
- [Key Features](#-key-features)
- [AI / ML Features](#-ai--ml-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [Getting Started](#-getting-started)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Deployment](#-deployment)
- [Origin Story](#-origin-story)
- [Author](#-author)

---

## 🔍 Overview

**BloodBank AI** is a production-grade, full-stack web application that digitizes and intelligentizes blood bank management. Built with Python Flask and PostgreSQL, it integrates **Facebook Prophet** for demand forecasting and **RandomForest** for donor eligibility classification replacing manual guesswork with data-driven decisions.

The platform manages the complete blood donation lifecycle:

Donor Registers → Books Appointment → Donates Blood
↓
Stock Auto-Updates → Request Received → Admin Approves
↓
Stock Deducted → Shortage Detected → Donors Notified

Originally developed as an Android application (Java + Firebase), it was redesigned as a full-stack web platform with ML capabilities to serve a broader audience.

> **Why this matters:** Blood shortages cost lives. This system predicts shortages before they happen, ensures only eligible donors donate, and automates the entire inventory workflow reducing human error in a critical healthcare context.

---

## 🚀 Live Demo

| Portal | URL | Credentials |
|--------|-----|-------------|
| 🔴 Landing Page | [blood-bank-web-app-5n5c.onrender.com](https://blood-bank-web-app-5n5c.onrender.com) | — |
| 🛡️ Admin Dashboard | [/admin/dashboard](https://blood-bank-web-app-5n5c.onrender.com/admin/dashboard) | `admin@bloodbank.com` / `admin123` |
| 👤 User Portal | [/user/dashboard](https://blood-bank-web-app-5n5c.onrender.com/user/dashboard) | `user1@bloodbank.com` / `user123` or `pradnesh@bloodbank.com` / `pradnesh123` |

> ⚠️ Hosted on Render.com free tier.
> First load may take 30 to 60 seconds to wake up.

---

## 📸 Screenshots

### 🏠 Landing Page
![Landing Page](screenshots/landing.png)

### 🛡️ Admin Dashboard
![Admin Dashboard](screenshots/admin_dashboard.png)

### 🩸 Blood Inventory
![Blood Stock](screenshots/blood_stock.png)

### 📋 Blood Request Management
![Requests](screenshots/requests.png)

### 📅 Appointment Booking
![Appointment Booking](screenshots/appointment_booking.png)

### 🤖 AI Demand Forecast Chart
![AI Forecast](screenshots/ai_forecast.png)

### 📢 Campaign Notice Board
![Campaigns](screenshots/campaigns.png)

### 📊 Reports and Analytics
![Reports](screenshots/reports.png)

---

## ✨ Key Features

### 👥 Role-Based Access Control

| Feature | Admin | User | Guest |
|---------|-------|------|-------|
| View blood stock | ✅ | ✅ | ✅ |
| Submit blood request | ✅ | ✅ | ❌ |
| Approve or Reject requests | ✅ | ❌ | ❌ |
| Add Edit Delete donors | ✅ | ❌ | ❌ |
| View AI forecast | ✅ | ❌ | ❌ |
| Manage campaigns | ✅ | ❌ | ❌ |
| Generate PDF reports | ✅ | ❌ | ❌ |
| Book donation appointment | ✅ | ✅ | ❌ |

### 🩸 Blood Request Workflow

- User submits request specifying blood group and quantity in units
- System checks real-time stock availability via AJAX before submit
- Admin approves and stock auto-deducts exactly the requested quantity
- If stock insufficient system shows shortage amount plus compatible alternatives plus donor contact list
- Email alert sent to admin when stock drops below 5 units or hits zero

### 📅 Donor Appointment System

- Donors book time slots Morning Afternoon or Evening
- Real-time eligibility check before booking confirms all of these:
  - Weight is 50 kg or above
  - Age is between 18 and 65
  - 6 or more months since last donation
  - Health status is Fit
- On appointment completion stock auto-increments for donor blood group
- Donor last donation date updates automatically
- Next eligible donation date 6 months forward displayed prominently

### ⚖️ Weight-Based Eligibility

- Weight field mandatory in donor registration
- Donors below 50 kg marked NOT ELIGIBLE with red badge
- Real-time weight indicator in donor form
- Eligibility badge shown on every donor card in registry
- Appointment booking blocked for underweight donors

### 📅 Next Donation Date Highlighter

- Automatically calculated as 6 months from last donation date
- Displayed as a highlighted card on donor profile
- Color coded: Green means eligible now, Yellow means days remaining
- Shows exact date and days remaining count
- Updates automatically when appointment is marked complete

### 📢 Campaign Notice Board

- Admin posts upcoming blood donation camp details
- Location date time target blood groups and organizer contact shown
- Highlighted Next Campaign hero banner on admin dashboard
- Countdown showing days until next campaign
- One-click appointment booking from campaign page

### 📄 PDF Report Generation

- Full inventory report generated with ReportLab
- Includes stock table donor summary request breakdown critical alerts
- Instant browser download with no third-party service needed

---

## 🤖 AI and ML Features

### 1. 📈 Blood Demand Forecasting using Facebook Prophet

```python
# Predicts units needed per blood group for next 7 days
# Based on historical request patterns
model = Prophet(daily_seasonality=True)
model.fit(historical_df)
forecast = model.predict(future_7_days)
```

- Model: Facebook Prophet time-series forecasting
- Input: Historical blood request data grouped by date
- Output: 7-day demand forecast with confidence intervals
- Display: Interactive Plotly.js line chart on admin dashboard
- Use case: Admin can pre-order stock before shortage hits

### 2. 🩺 Donor Eligibility Classifier using RandomForest

```python
# Predicts donor eligibility from health features
features = [age, days_since_last_donation,
            health_status, weight]
model = RandomForestClassifier(n_estimators=100)
prediction = model.predict([donor_features])
confidence = model.predict_proba([donor_features]).max()
```

- Model: RandomForest Classifier from scikit-learn
- Features: Age weight days since last donation health status
- Output: Eligible or Not Eligible plus confidence percentage
- Display: Color-coded badge on each donor card
- Weight Rule: Hard constraint — weight below 50 kg means Not Eligible

### 3. 🧠 Smart Stock Alert System

```python
# Goes beyond simple threshold of less than 5 units
# Factors in current stock average daily demand
# pending requests and days until estimated stockout
days_until_empty = effective_stock / avg_daily_demand
```

- Logic: ML-driven threshold vs simple less than 5 units rule
- Output: Safe Warning Low Critical with estimated days until stockout
- Display: Color-coded stock cards with smart alert messages

### 4. 🔄 Blood Compatibility Suggester

```python
COMPATIBILITY_MAP = {
    'O-': ['A+','A-','B+','B-','O+','O-','AB+','AB-'],
    'O+': ['A+','B+','O+','AB+'],
    # all 8 groups mapped
}
```

- When requested blood group is out of stock
- Suggests compatible alternatives ranked by current availability
- Lists donors of compatible groups with direct contact information

---

## 🏗️ System Architecture

┌─────────────────────────────────────────────────────┐
│ USERS │
│ Admin User / Donor │
└──────────────┬──────────────────────┬───────────────┘
│ │
┌──────────────▼──────────────────────▼───────────────┐
│ FRONTEND Jinja2 + Tailwind CSS │
│ Landing Dashboard Donors Stock Requests │
│ Appointments Campaigns Reports │
│ Plotly.js Charts AJAX Material Symbols │
└──────────────────────────┬──────────────────────────┘
│
┌──────────────────────────▼──────────────────────────┐
│ FLASK APPLICATION Python 3.11 │
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│ │ Routes │ │ Models │ │ ML / AI Engine │ │
│ │ 8 BPs │ │ ORM │ │ Prophet RF │ │
│ └──────────┘ └──────────┘ └──────────────────┘ │
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│ │ Auth │ │ Utils │ │ Flask-Mail │ │
│ │ bcrypt │ │ PDF │ │ Email Alerts │ │
│ └──────────┘ └──────────┘ └──────────────────┘ │
└──────────────────────────┬──────────────────────────┘
│
┌──────────────────────────▼──────────────────────────┐
│ PostgreSQL DATABASE │
│ │
│ users donors blood_stock blood_requests │
│ appointments campaigns │
└─────────────────────────────────────────────────────┘


---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11+ | Core language |
| Flask | 3.0.0 | Web framework |
| SQLAlchemy | 2.0.23 | ORM |
| Flask-Migrate | 4.0.5 | DB migrations |
| Flask-Login | 0.6.3 | Session authentication |
| Flask-Bcrypt | 1.0.1 | Password hashing |
| Flask-Mail | 0.9.1 | Email alerts |
| Gunicorn | 21.2.0 | Production WSGI server |

### Database

| Technology | Purpose |
|-----------|---------|
| PostgreSQL 16 | Primary cloud database |
| psycopg2-binary | PostgreSQL Python driver |

### AI and ML

| Library | Version | Purpose |
|---------|---------|---------|
| scikit-learn | 1.3.2 | RandomForest classifier |
| Prophet | 1.1.5 | Time-series demand forecasting |
| pandas | 2.1.4 | Data manipulation |
| numpy | 1.26.2 | Numerical operations |
| python-dateutil | 2.8.2 | Next donation date calculation |

### Frontend

| Technology | Purpose |
|-----------|---------|
| Tailwind CSS | Utility-first dark theme styling |
| Plotly.js | Interactive analytics charts |
| Material Symbols | Google icon system |
| Manrope Google Fonts | Typography |
| Vanilla JavaScript | AJAX and interactivity |

### DevOps and Deployment

| Tool | Purpose |
|------|---------|
| Render.com | Cloud hosting free tier |
| GitHub | Version control and CI/CD |
| Flask-Migrate | Zero-downtime migrations |
| python-dotenv | Environment variable management |

---

## 🗃️ Database Schema

```sql
-- 6 core tables

users
  id, name, email, password_hash, role,
  blood_group, phone, created_at

donors
  id, name, age, phone, address, blood_group,
  weight, last_donation_date, health_status,
  notes, created_at

blood_stock
  id, blood_group, units, last_updated

blood_requests
  id, requester_name, blood_group, quantity,
  hospital_name, urgency, required_date,
  notes, status, user_id, created_at

appointments
  id, donor_id, appointment_date, slot,
  blood_group, units_to_donate, status,
  units_donated, stock_updated_at, created_at

campaigns
  id, title, location, address, campaign_date,
  campaign_time, description, target_blood_groups,
  target_donors, organizer_name, organizer_phone,
  is_active, created_at
```

---

## 🚀 Getting Started

### Prerequisites

Python 3.11+
PostgreSQL 14+
Git


### Step 1 — Clone the Repository

```bash
git clone https://github.com/Pradnesh02/Blood-Bank-Web-app.git
cd Blood-Bank-Web-app
```

### Step 2 — Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac or Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set Up Environment Variables

```bash
cp .env.example .env
```

Edit your .env file with these values:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-very-long-random-secret-key-here
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/bloodbank_db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
ADMIN_EMAIL=admin@bloodbank.com
```

### Step 5 — Create PostgreSQL Database

```sql
CREATE DATABASE bloodbank_db;
CREATE USER bloodbank_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE bloodbank_db TO bloodbank_user;
\c bloodbank_db
GRANT ALL ON SCHEMA public TO bloodbank_user;
```

### Step 6 — Run Migrations

```bash
flask db upgrade
```

### Step 7 — Start the Application

```bash
flask run
```

### Step 8 — Open in Browser

Landing Page: http://localhost:5000
Admin Dashboard: http://localhost:5000/admin/dashboard
User Portal: http://localhost:5000/user/dashboard


---

## 📁 Project Structure

bloodbank-web/
│
├── app/
│ ├── init.py
│ ├── config.py
│ │
│ ├── models/
│ │ ├── user.py
│ │ ├── donor.py
│ │ ├── blood_stock.py
│ │ ├── request.py
│ │ ├── appointment.py
│ │ └── campaign.py
│ │
│ ├── routes/
│ │ ├── auth.py
│ │ ├── admin.py
│ │ ├── user.py
│ │ ├── donors.py
│ │ ├── stock.py
│ │ ├── requests.py
│ │ ├── reports.py
│ │ ├── appointments.py
│ │ ├── campaigns.py
│ │ └── ml.py
│ │
│ ├── ml/
│ │ ├── forecasting.py
│ │ ├── eligibility.py
│ │ ├── stock_alert.py
│ │ └── compatibility.py
│ │
│ ├── templates/
│ │ ├── base.html
│ │ ├── landing.html
│ │ ├── auth/
│ │ ├── admin/
│ │ ├── user/
│ │ ├── appointments/
│ │ └── campaigns/
│ │
│ ├── static/
│ │ ├── css/
│ │ └── js/
│ │
│ └── utils/
│ ├── pdf_generator.py
│ └── email_alerts.py
│
├── migrations/
├── screenshots/
├── tests/
│ ├── test_routes.py
│ └── test_ml.py
├── .env.example
├── .gitignore
├── Procfile
├── render.yaml
├── requirements.txt
└── run.py


---

## 📡 API Endpoints

### Authentication

POST /auth/login
POST /auth/register
GET /auth/logout


### Donors

GET /donors/
POST /donors/add
PUT /donors/<id>/edit
POST /donors/<id>/delete
GET /donors/search


### Blood Stock

GET /stock/
POST /stock/update
GET /stock/api/levels


### Blood Requests

POST /requests/submit
POST /requests/<id>/approve
POST /requests/<id>/reject
GET /requests/api/check-stock


### Appointments

GET /appointments/book
POST /appointments/book
GET /appointments/
POST /appointments/<id>/complete
POST /appointments/<id>/cancel
GET /appointments/api/slots
GET /appointments/api/check-eligibility


### AI and ML

GET /ml/forecast
GET /ml/eligibility/<id>
GET /ml/smart-alert
GET /ml/compatibility/<group>


### Reports

GET /reports/
GET /reports/pdf
GET /reports/api/data


### Campaigns

GET /campaigns/
POST /campaigns/add
POST /campaigns/<id>/delete
GET /campaigns/api/next


---

## ☁️ Deployment on Render.com

### Step 1 — Push to GitHub

```bash
git add .
git commit -m "Production release v1.0"
git push origin main
```

### Step 2 — Create account at render.com

### Step 3 — New Web Service and connect your GitHub repo

### Step 4 — Configure these settings

Environment: Python
Build Command: pip install -r requirements.txt
Start Command: flask db upgrade && gunicorn run:app


### Step 5 — Add Environment Variables in Render dashboard

SECRET_KEY → generate a long random string
DATABASE_URL → auto-filled from Render PostgreSQL
FLASK_ENV → production
MAIL_USERNAME → your Gmail address
MAIL_PASSWORD → your Gmail app password
ADMIN_EMAIL → admin alert email


### Step 6 — Add Render PostgreSQL

New → PostgreSQL → Free tier → Name it bloodbank-postgres
Copy the Internal Database URL and paste it as DATABASE_URL

### Step 7 — Click Deploy

### Keep Free Tier Awake

Add your live URL to UptimeRobot at uptimerobot.com which is free
Set it to ping every 5 minutes
This prevents Render free tier from sleeping

---

## 📱 Origin — From Android to Web

This web application was converted from an Android app built in Java and XML layouts with Firebase and SQLite.

| Android Version | Web Version |
|----------------|-------------|
| Java + XML layouts | Python Flask + Jinja2 |
| Firebase Realtime DB | PostgreSQL + SQLAlchemy |
| Firebase Auth | Flask-Login + bcrypt |
| Android NotificationManager | Flask-Mail email alerts |
| Android PdfDocument API | ReportLab |
| MPAndroidChart | Plotly.js |
| SQLite local storage | PostgreSQL cloud database |

---

## 🧑💻 Author

**Pradnesh Prasad Khasnis**
AI Engineering Student and Full Stack Developer

[GitHub](https://github.com/Pradnesh02)
[Email](mailto:kprady02@gmail.com)

Built with love and lots of coffee — Maharashtra, India

---

## 📄 License

MIT License

Copyright 2026 Pradnesh Prasad Khasnis

Permission is hereby granted free of charge to any person obtaining a copy of this software to use copy modify and distribute it subject to the MIT License conditions.

---

If this project helped you please give it a star on GitHub. It helps others discover the project and motivates continued development.  
