# HRMS - Human Resource Management System

A comprehensive SaaS CMS for IT Company Management built with Django and Django Rest Framework.

## Features

- **Multi-Role System**: CEO, HR, Project Manager, Developer, UI/UX Designer, BDE
- **Project Management**: Full project lifecycle management
- **Task Management**: Kanban boards and task tracking
- **Attendance Management**: Track employee attendance
- **Leave Management**: Leave requests and approvals
- **Payroll Management**: Salary and payroll processing
- **CRM/Leads Management**: Business development pipeline
- **Daily Updates**: Team daily work updates
- **Notifications**: In-app notification system
- **Audit Logs**: Complete audit trail
- **Reports**: PDF/CSV export functionality

## Technology Stack

- **Backend**: Django 6.0.1, Django Rest Framework
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: JWT (Simple JWT)
- **API Documentation**: Swagger/OpenAPI (drf-yasg)
- **Task Queue**: Celery with Redis
- **PDF Generation**: ReportLab, WeasyPrint

## Project Structure

```
hrms/
├── backend/              # Main Django project
│   ├── settings.py      # Project settings
│   ├── urls.py          # Main URL configuration
│   └── ...
├── accounts/            # User authentication and roles
├── organizations/        # Multi-tenancy support
├── projects/            # Project management
├── tasks/               # Task management
├── attendance/          # Attendance tracking
├── leaves/              # Leave management
├── payroll/             # Payroll management
├── daily_updates/       # Daily work updates
├── leads_crm/           # CRM and leads management
├── notifications/       # Notification system
├── reports/             # Report generation
├── auditlogs/           # Audit logging
├── templates/           # Django templates
├── static/              # Static files (CSS, JS)
├── media/               # Media files
├── .env                 # Environment variables
├── requirements.txt     # Python dependencies
└── manage.py            # Django management script
```

## Installation & Setup

### Prerequisites

- Python 3.13+
- PostgreSQL
- Redis (for Celery)
- Virtual environment

### Step 1: Clone and Setup Virtual Environment

```bash
# Navigate to project directory
cd hrms

# Activate virtual environment (already created as 'env')
source env/bin/activate  # On macOS/Linux
# or
env\Scripts\activate  # On Windows
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Edit the `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=hrms_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 4: Database Setup

**Option 1: SQLite (Default - Recommended for Development)**
- SQLite is already configured in `settings.py`
- No additional setup required
- Database file: `db.sqlite3` (created automatically)

**Option 2: PostgreSQL (For Production)**
- Uncomment PostgreSQL configuration in `settings.py`
- Create database:
  ```bash
  createdb hrms_db
  # Or using psql
  psql -U postgres
  CREATE DATABASE hrms_db;
  ```
- Update `.env` file with PostgreSQL credentials

### Step 5: Run Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Step 6: Create Superuser (CEO)

```bash
python manage.py createsuperuser
```

Follow the prompts to create a CEO/admin user.

### Step 7: Create Initial Roles

You can create roles via Django admin or use a management command:

```bash
python manage.py shell
```

```python
from accounts.models import Role

roles = [
    {'name': 'CEO', 'display_name': 'CEO', 'description': 'Chief Executive Officer'},
    {'name': 'HR', 'display_name': 'HR', 'description': 'Human Resources'},
    {'name': 'PM', 'display_name': 'Project Manager', 'description': 'Project Manager'},
    {'name': 'DEV', 'display_name': 'Developer', 'description': 'Developer'},
    {'name': 'UIUX', 'display_name': 'UI/UX Designer', 'description': 'UI/UX Designer'},
    {'name': 'BDE', 'display_name': 'Business Development Executive', 'description': 'BDE'},
]

for role_data in roles:
    Role.objects.get_or_create(**role_data)
```

### Step 8: Run Development Server

```bash
# Run on default port 8000
python manage.py runserver

# Or run on port 8001
python manage.py runserver 8001

# Or use the helper script (macOS/Linux)
./runserver.sh

# Or use the helper script (Windows)
runserver.bat
```

The application will be available at:
- `http://localhost:8000` (default port)
- `http://localhost:8001` (if using port 8001)

### Step 9: Access API Documentation

If running on port 8001:
- Swagger UI: `http://localhost:8001/swagger/`
- ReDoc: `http://localhost:8001/redoc/`
- Admin Panel: `http://localhost:8001/admin/`

If running on default port 8000:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- Admin Panel: `http://localhost:8000/admin/`

## Folder Structure for Models, Views, and Serializers

Each app follows a modular structure:

```
app_name/
├── models/
│   ├── __init__.py
│   ├── model1.py
│   └── model2.py
├── views/
│   ├── __init__.py
│   ├── view1.py
│   └── view2.py
├── serializers/
│   ├── __init__.py
│   ├── serializer1.py
│   └── serializer2.py
├── models.py          # Imports from models/
├── views.py           # Imports from views/
└── urls.py
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user (CEO only)
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/refresh/` - Refresh JWT token

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project (CEO)
- `GET /api/projects/{id}/` - Project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### And more...

See Swagger documentation for complete API reference.

## Role-Based Access Control

### CEO
- Full admin access
- Create/edit/delete projects
- Manage users and roles
- View all reports and data

### HR
- Manage attendance
- Approve/reject leaves
- Manage payroll
- View employee profiles

### Project Manager
- Manage assigned projects
- Assign tasks to Dev/UIUX
- View daily updates
- Update project status

### Developer
- View assigned projects
- Update task statuses
- Submit daily updates
- Apply for leaves

### UI/UX Designer
- Same as Developer
- Upload design assets
- Add Figma links

### BDE
- Manage leads pipeline
- Create proposals
- Log meetings
- View project overview

## Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files

```bash
python manage.py collectstatic
```

## Deployment

### Production Settings

1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` with your domain
3. Use a production database
4. Configure proper email settings
5. Set up SSL/HTTPS
6. Use Gunicorn + Nginx for production

### Docker (Optional)

Docker setup can be added for containerized deployment.

## License

This project is proprietary software.

## Support

For issues and questions, please contact the development team.
