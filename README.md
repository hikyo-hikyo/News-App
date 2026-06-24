# NewsApp - Django News Platform

A full-featured news application where independent journalists and publishers can publish articles, editors can review and approve content, and readers can browse and subscribe to their favorite sources.

Built with **Django**, **Django REST Framework**, role-based access control, and MariaDB.

---

## Features

### For Readers
- Browse approved articles
- Subscribe to publishers and independent journalists
- View curated newsletters
- Clean, responsive frontend interface

### For Journalists
- Create and manage their own articles
- Publish independent articles or under a publisher
- Create newsletters from approved articles
- View their published content

### For Editors
- Review pending articles
- Approve or reject articles for publishing
- Manage content quality

### Technical Features
- **Role-based authentication** (Reader, Journalist, Editor) using Django Groups
- Custom User model with conditional fields (subscriptions)
- Article approval workflow with **Django Signals**
- Full **RESTful API** with JWT authentication
- MariaDB database support
- Responsive Bootstrap frontend

---

## Tech Stack

- **Backend**: Django 5.0+
- **API**: Django REST Framework + SimpleJWT
- **Database**: MariaDB (MySQL backend)
- **Authentication**: Custom User Model + Group-based permissions
- **Frontend**: Django Templates + Bootstrap 5
- **Signals**: Post-approval email notifications + external webhook simulation

---

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/hikyo-hikyo/News-App.git
cd News-App
```

### 2. Requirements
```bash
pip install -r requirements.txt
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py populate_db
python manage.py runserver
```