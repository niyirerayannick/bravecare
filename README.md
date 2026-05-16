# BraveCare Outreach Management System

A professional healthcare outreach management dashboard built with **Django** and **Tailwind CSS**. Designed for community health organizations to manage patients, outreach campaigns, volunteers, and communications.

---

## Features

- **Dashboard** — Real-time KPIs, Chart.js visualizations, follow-up tables, volunteer activity panel
- **Patient Management** — Full CRUD, risk stratification, screening history, MCH records
- **Outreach Campaigns** — Create and track community health campaigns with progress bars
- **Screening Records** — Log and track patient screenings by type and result
- **Maternal & Child Health** — Track antenatal, postnatal, immunization, and nutrition services
- **Volunteer Management** — Manage community health workers and field staff
- **Communication Center** — Send SMS reminders, outreach announcements, follow-up notifications
- **Reports & Analytics** — Data-driven charts across all modules
- **Role-Based Access** — Admin, Coordinator, Healthcare Worker, Volunteer, Data Manager
- **Django Admin** — Full backend data management

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Frontend | Django Templates + Tailwind CSS (CDN) |
| Charts | Chart.js 4.4 |
| Icons | Font Awesome 6.5 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Auth | Django built-in authentication |

---

## Quick Start

### 1. Clone / Navigate to project

```bash
cd bravecare
```

### 2. Create virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run database migrations

```bash
python manage.py migrate
```

### 5. Seed demo data

```bash
python manage.py seed_data
```

This creates:
- **Admin user**: `admin` / `admin123`
- 25 sample patients with screenings, follow-ups, and MCH records
- 6 outreach campaigns (active, planned, completed)
- 10 volunteers with task history
- 5 communication messages

### 6. Start the development server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

Login with: **admin / admin123**

---

## Project Structure

```
bravecare/
├── bravecare_outreach/        # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                      # Dashboard app
│   ├── management/commands/
│   │   └── seed_data.py       # Demo data generator
│   ├── views.py
│   └── urls.py
├── accounts/                  # Authentication & user profiles
├── patients/                  # Patients, screenings, follow-ups, MCH
├── outreach/                  # Outreach campaigns
├── volunteers/                # Volunteer management
├── communication/             # Communication center
├── reports/                   # Analytics & reports
├── templates/                 # HTML templates (Django + Tailwind)
│   ├── base.html              # Master layout with sidebar
│   ├── registration/
│   │   └── login.html
│   ├── core/dashboard.html
│   ├── patients/
│   ├── outreach/
│   ├── volunteers/
│   ├── communication/
│   └── reports/
├── static/
│   ├── css/custom.css
│   └── js/custom.js
├── manage.py
└── requirements.txt
```

---

## User Roles

| Role | Description |
|------|-------------|
| **Admin** | Full system access, user management |
| **Outreach Coordinator** | Manage campaigns, volunteers, reports |
| **Healthcare Worker** | Patient records, screenings, follow-ups |
| **Volunteer** | View assignments, update task status |
| **Data Manager** | Reports, data entry, patient records |

---

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Main dashboard |
| `/patients/` | Patient list |
| `/patients/add/` | Add new patient |
| `/outreach/` | Outreach campaigns |
| `/outreach/add/` | New campaign |
| `/patients/screenings/` | Screening records |
| `/patients/followups/` | Follow-up tracking |
| `/volunteers/` | Volunteer management |
| `/communication/` | Communication center |
| `/reports/` | Analytics & reports |
| `/admin/` | Django admin panel |
| `/accounts/login/` | Login page |

---

## Seed Data Options

```bash
# Seed with fresh data (adds on top of existing)
python manage.py seed_data

# Clear all demo data and reseed
python manage.py seed_data --clear
```

---

## Production Setup

1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Switch to PostgreSQL:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'bravecare_db',
           'USER': 'your_user',
           'PASSWORD': 'your_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
5. Install: `pip install psycopg2-binary`
6. Run: `python manage.py collectstatic`

---

## License

Built for BraveCare Outreach — Healthcare Outreach Management.
