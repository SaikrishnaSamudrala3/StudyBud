# StudyBud

A Django-based web application designed to connect people with similar study interests.  
**StudyBud** helps users find others who share their study goals and create a personalized favorites list to track preferred study partners.

---

## Features

- Connect with users who share similar study topics.  
- Add and manage favorite study buddies.  
- User authentication and session management.  
- Real-time chat rooms (if configured).  
- Responsive design built with HTML, CSS, and Django templates.  
- SQLite database for fast local setup.

---

## Prerequisites

Before running the app, ensure you have:

- **Python 3.9+**  
- **Django 4.x+**  
- **Git**  
- (Optional) A virtual environment tool such as `venv` or `virtualenv`.

---

## Installation & Setup

```bash
# Clone the repository
git clone https://github.com/SaikrishnaSamudrala3/StudyBud.git
cd StudyBud

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # (Windows: .venv\Scripts\activate)

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# (Optional) Create a superuser to access the admin panel
python manage.py createsuperuser
