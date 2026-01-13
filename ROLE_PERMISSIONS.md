# HRMS Role Permissions Documentation

Complete list of permissions for each role in the HRMS system.

## Permission Structure

Each role has permissions organized by module:
- **users**: User management
- **projects**: Project management
- **tasks**: Task management
- **attendance**: Attendance tracking
- **leaves**: Leave management
- **payroll**: Payroll management
- **daily_updates**: Daily work updates
- **leads**: Leads/CRM management
- **reports**: Report generation
- **notifications**: Notification system
- **audit_logs**: Audit log viewing

---

## CEO (Chief Executive Officer)

**Full admin access to everything**

### Users
- ✓ Create users
- ✓ Read all users
- ✓ Update users
- ✓ Delete users
- ✓ Assign roles
- ✓ View all users

### Projects
- ✓ Create projects
- ✓ Read all projects
- ✓ Update projects
- ✓ Delete projects
- ✓ Assign team members
- ✓ View all projects
- ✓ Change project status
- ✓ View budget information

### Tasks
- ✓ Create tasks
- ✓ Read all tasks
- ✓ Update tasks
- ✓ Delete tasks
- ✓ Assign to anyone
- ✓ View all tasks
- ✓ Change task status

### Attendance
- ✗ Create attendance (HR only)
- ✓ Read all attendance
- ✗ Update attendance (HR only)
- ✗ Delete attendance
- ✓ View all attendance
- ✓ View attendance reports

### Leaves
- ✗ Create leave (employees only)
- ✓ Read all leaves
- ✗ Update leave
- ✗ Delete leave
- ✗ Approve/reject leave (HR only)
- ✓ View all leaves
- ✓ View leave calendar

### Payroll
- ✗ Create payroll (HR only)
- ✓ Read all payroll
- ✓ Update payroll (can override if necessary)
- ✗ Delete payroll
- ✓ View all payroll
- ✓ View salary summary
- ✗ Generate payslip (HR only)

### Daily Updates
- ✗ Create updates (Dev/UIUX only)
- ✓ Read all updates
- ✗ Update updates
- ✗ Delete updates
- ✓ View all updates
- ✓ View timeline

### Leads
- ✓ Create leads
- ✓ Read all leads
- ✓ Update leads
- ✓ Delete leads
- ✓ View all leads
- ✓ Convert lead to project
- ✓ View lead reports

### Reports
- ✓ Generate all reports
- ✓ View all reports
- ✓ Export to PDF
- ✓ Export to CSV

### Notifications
- ✓ Create notifications
- ✓ Read all notifications
- ✓ View all notifications

### Audit Logs
- ✓ View all audit logs

---

## HR (Human Resources)

**Manages attendance, leaves, and payroll**

### Users
- ✗ Create users
- ✓ Read all users (view profiles)
- ✗ Update users (can update employee info, not roles)
- ✗ Delete users
- ✗ Assign roles
- ✓ View all users
- ✓ View employee profiles

### Projects
- ✗ Create projects
- ✓ Read projects (limited - only for context)
- ✗ Update projects
- ✗ Delete projects
- ✗ Assign team
- ✓ View all projects (read-only)
- ✗ Change status
- ✗ View budget

### Tasks
- ✗ Create tasks
- ✗ Read tasks (no access to project internals)
- ✗ Update tasks
- ✗ Delete tasks
- ✗ Assign tasks
- ✗ View tasks

### Attendance
- ✓ Create attendance
- ✓ Read all attendance
- ✓ Update attendance
- ✓ Delete attendance
- ✓ View all attendance
- ✓ Mark attendance
- ✓ View attendance reports
- ✓ Export attendance reports

### Leaves
- ✗ Create leave
- ✓ Read all leaves
- ✗ Update leave
- ✗ Delete leave
- ✓ Approve leave
- ✓ Reject leave
- ✓ View all leaves
- ✓ View leave calendar
- ✓ Manage leave balances

### Payroll
- ✓ Create payroll
- ✓ Read all payroll
- ✓ Update payroll
- ✓ Delete payroll
- ✓ View all payroll
- ✓ Calculate salary
- ✓ Generate payslip
- ✓ Export payroll reports

### Daily Updates
- ✗ Create updates
- ✗ Read updates (no access)
- ✗ Update updates
- ✗ Delete updates

### Leads
- ✗ Create leads
- ✗ Read leads
- ✗ Update leads
- ✗ Delete leads

### Reports
- ✓ Generate reports
- ✓ View all reports
- ✓ Export to PDF
- ✓ Export to CSV
- ✓ Attendance reports
- ✓ Payroll reports
- ✓ Leave reports

### Notifications
- ✓ Create notifications
- ✓ Read notifications
- ✓ View all notifications

### Audit Logs
- ✓ View all audit logs
- ✓ View attendance logs
- ✓ View payroll logs
- ✓ View leave logs

---

## PM (Project Manager)

**Manages assigned projects and tasks**

### Users
- ✗ Create users
- ✓ Read users (only team members)
- ✗ Update users
- ✗ Delete users
- ✗ Assign roles
- ✗ View all users
- ✓ View team members

### Projects
- ✗ Create projects
- ✓ Read projects (assigned projects)
- ✓ Update projects (only assigned projects)
- ✗ Delete projects
- ✓ Assign team (can assign Dev/UIUX to assigned projects)
- ✗ View all projects
- ✓ View assigned projects
- ✓ Change project status
- ✓ View budget

### Tasks
- ✓ Create tasks
- ✓ Read tasks (project tasks)
- ✓ Update tasks
- ✓ Delete tasks
- ✗ Assign to anyone
- ✓ Assign Dev/UIUX
- ✗ View all tasks
- ✓ View project tasks
- ✓ Change task status

### Attendance
- ✗ Create attendance
- ✗ Read attendance
- ✗ Update attendance
- ✗ Delete attendance

### Leaves
- ✗ Create leave
- ✗ Read leaves
- ✗ Update leaves
- ✗ Delete leaves
- ✗ Approve/reject leave

### Payroll
- ✗ Create payroll
- ✗ Read payroll
- ✗ Update payroll
- ✗ Delete payroll

### Daily Updates
- ✗ Create updates
- ✓ Read updates (for assigned projects)
- ✗ Update updates
- ✗ Delete updates
- ✗ View all updates
- ✓ View project updates

### Leads
- ✗ Create leads
- ✗ Read leads
- ✗ Update leads
- ✗ Delete leads

### Reports
- ✗ Generate reports
- ✗ View all reports
- ✓ View project reports

### Notifications
- ✓ Create notifications
- ✓ Read notifications
- ✗ View all notifications

### Audit Logs
- ✗ View all audit logs
- ✓ View project audit logs

---

## DEV (Developer)

**Works on assigned projects and tasks**

### Users
- ✗ Create users
- ✗ Read users
- ✗ Update users
- ✗ Delete users
- ✓ View own profile

### Projects
- ✗ Create projects
- ✓ Read projects (read-only, all projects)
- ✗ Update projects
- ✗ Delete projects
- ✗ Assign team
- ✓ View all projects (read-only)
- ✓ View assigned projects

### Tasks
- ✗ Create tasks
- ✓ Read tasks (assigned tasks)
- ✓ Update tasks (own tasks)
- ✗ Delete tasks
- ✗ Assign tasks
- ✗ View all tasks
- ✓ View assigned tasks
- ✓ Change status (assigned tasks)

### Attendance
- ✗ Create attendance
- ✓ Read attendance (own attendance only)
- ✗ Update attendance
- ✗ Delete attendance
- ✓ View own attendance

### Leaves
- ✓ Create leave
- ✓ Read leaves (own leaves only)
- ✓ Update leave (pending leaves)
- ✓ Delete leave (pending leaves)
- ✗ Approve/reject leave
- ✓ View own leaves

### Payroll
- ✗ Create payroll
- ✗ Read payroll
- ✗ Update payroll
- ✗ Delete payroll
- ✗ View own payroll

### Daily Updates
- ✓ Create updates
- ✓ Read updates (own updates)
- ✓ Update updates (own updates)
- ✓ Delete updates (own updates)
- ✓ View own updates
- ✓ View project updates (assigned projects)

### Leads
- ✗ Create leads
- ✗ Read leads
- ✗ Update leads
- ✗ Delete leads

### Reports
- ✗ Generate reports
- ✗ View reports

### Notifications
- ✗ Create notifications
- ✓ Read notifications (own notifications)
- ✓ View own notifications

### Audit Logs
- ✗ View audit logs

---

## UIUX (UI/UX Designer)

**Works on design tasks and assets**

### Users
- ✗ Create users
- ✗ Read users
- ✗ Update users
- ✗ Delete users
- ✓ View own profile

### Projects
- ✗ Create projects
- ✓ Read projects (read-only, all projects)
- ✗ Update projects
- ✗ Delete projects
- ✗ Assign team
- ✓ View all projects (read-only)
- ✓ View assigned projects

### Tasks
- ✗ Create tasks
- ✓ Read tasks (assigned design tasks)
- ✓ Update tasks (own design tasks)
- ✗ Delete tasks
- ✗ Assign tasks
- ✗ View all tasks
- ✓ View assigned tasks
- ✓ Change status (assigned tasks)
- ✓ Upload design assets
- ✓ Add Figma links

### Attendance
- ✗ Create attendance
- ✓ Read attendance (own attendance only)
- ✗ Update attendance
- ✗ Delete attendance
- ✓ View own attendance

### Leaves
- ✓ Create leave
- ✓ Read leaves (own leaves only)
- ✓ Update leave (pending leaves)
- ✓ Delete leave (pending leaves)
- ✗ Approve/reject leave
- ✓ View own leaves

### Payroll
- ✗ Create payroll
- ✗ Read payroll
- ✗ Update payroll
- ✗ Delete payroll
- ✗ View own payroll

### Daily Updates
- ✓ Create updates
- ✓ Read updates (own updates)
- ✓ Update updates (own updates)
- ✓ Delete updates (own updates)
- ✓ View own updates
- ✓ View project updates (assigned projects)
- ✓ Upload assets
- ✓ Add Figma links

### Leads
- ✗ Create leads
- ✗ Read leads
- ✗ Update leads
- ✗ Delete leads

### Reports
- ✗ Generate reports
- ✗ View reports

### Notifications
- ✗ Create notifications
- ✓ Read notifications (own notifications)
- ✓ View own notifications

### Audit Logs
- ✗ View audit logs

---

## BDE (Business Development Executive)

**Manages leads and business development**

### Users
- ✗ Create users
- ✗ Read users
- ✗ Update users
- ✗ Delete users
- ✓ View own profile

### Projects
- ✗ Create projects
- ✓ Read projects (read-only overview)
- ✗ Update projects
- ✗ Delete projects
- ✗ Assign team
- ✓ View all projects (read-only overview)
- ✓ Recommend projects to CEO

### Tasks
- ✗ Create tasks
- ✗ Read tasks
- ✗ Update tasks
- ✗ Delete tasks

### Attendance
- ✗ Create attendance
- ✓ Read attendance (own attendance only)
- ✗ Update attendance
- ✗ Delete attendance
- ✓ View own attendance

### Leaves
- ✓ Create leave
- ✓ Read leaves (own leaves only)
- ✓ Update leave (pending leaves)
- ✓ Delete leave (pending leaves)
- ✗ Approve/reject leave
- ✓ View own leaves

### Payroll
- ✗ Create payroll
- ✗ Read payroll
- ✗ Update payroll
- ✗ Delete payroll
- ✗ View own payroll

### Daily Updates
- ✗ Create updates
- ✗ Read updates
- ✗ Update updates
- ✗ Delete updates

### Leads
- ✓ Create leads
- ✓ Read all leads
- ✓ Update leads
- ✓ Delete leads
- ✓ View all leads
- ✓ Manage leads pipeline
- ✓ Create proposals
- ✓ Log meetings
- ✗ Convert to project (can recommend, CEO converts)

### Reports
- ✗ Generate all reports
- ✗ View all reports
- ✓ View lead reports
- ✓ View conversion reports

### Notifications
- ✗ Create notifications
- ✓ Read notifications (own notifications)
- ✓ View own notifications

### Audit Logs
- ✗ View all audit logs
- ✓ View lead-related audit logs

---

## Permission Checking

### In Views
```python
from accounts.utils import has_permission, permission_required

# Using decorator
@permission_required('projects', 'create')
def create_project(request):
    # Only users with project create permission can access
    pass

# In view logic
if has_permission(request.user, 'tasks', 'assign_anyone'):
    # Can assign tasks to anyone
    pass
else:
    # Can only assign to Dev/UIUX
    pass
```

### In Templates
```django
{% if user|has_permission:'projects' 'create' %}
    <a href="{% url 'projects:create' %}">Create Project</a>
{% endif %}
```

---

## Setup Roles

To create roles with permissions, run:
```bash
python manage.py setup_roles
```

To view all permissions:
```bash
python manage.py show_permissions
```

---

## Notes

- **CEO** has full override access to everything
- **HR** has no access to project internals (tasks, daily updates)
- **PM** can only manage assigned projects
- **DEV/UIUX** have similar permissions but UIUX can upload assets
- **BDE** has full access to leads but read-only project overview
- All roles can view their own attendance and apply for leaves
- Only HR can manage attendance and payroll
- Only CEO can create users and assign roles
