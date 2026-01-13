# HRMS Role Permissions - Quick Reference

## Permission Matrix

| Module | Action | CEO | HR | PM | DEV | UIUX | BDE |
|--------|--------|-----|----|----|-----|------|-----|
| **Users** |
| Create | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Read All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Update | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Delete | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Assign Role | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Projects** |
| Create | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Read All | ✓ | ✓* | ✗ | ✓ | ✓ | ✓* |
| Update | ✓ | ✗ | ✓** | ✗ | ✗ | ✗ |
| Delete | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Assign Team | ✓ | ✗ | ✓** | ✗ | ✗ | ✗ |
| **Tasks** |
| Create | ✓ | ✗ | ✓** | ✗ | ✗ | ✗ |
| Read All | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Update | ✓ | ✗ | ✓** | ✓*** | ✓*** | ✗ |
| Delete | ✓ | ✗ | ✓** | ✗ | ✗ | ✗ |
| Assign Anyone | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Attendance** |
| Create | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Read All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Update | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Read Own | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Leaves** |
| Create | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| Read All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Approve/Reject | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Read Own | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Payroll** |
| Create | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Read All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Update | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Generate Payslip | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| **Daily Updates** |
| Create | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| Read All | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Read Project | ✓ | ✗ | ✓** | ✓*** | ✓*** | ✗ |
| **Leads** |
| Create | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Read All | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Update | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Delete | ✓ | ✗ | ✗ | ✗ | ✗ | ✓ |
| Convert to Project | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| **Reports** |
| Generate All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| View All | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| Export PDF/CSV | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |

**Notes:**
- * = Limited read-only access (for context only)
- ** = Only for assigned projects
- *** = Only for assigned tasks/updates

## Key Differences

### CEO
- **Full access** to everything
- Can create users and assign roles
- Can override any restriction
- Can view all reports and audit logs

### HR
- **No access** to project internals (tasks, daily updates)
- **Full access** to attendance, leaves, payroll
- Can view employee profiles but cannot change roles
- Can generate HR-related reports

### PM
- **Limited to assigned projects only**
- Can assign Dev/UIUX to assigned projects
- Can create/update tasks in assigned projects
- Can view daily updates for assigned projects
- **No access** to attendance, leaves, payroll

### DEV
- **Read-only** access to all projects
- Can update **assigned tasks** only
- Can submit **daily updates**
- Can apply for **leaves**
- Can view **own attendance**

### UIUX
- **Same as DEV** plus:
- Can upload **design assets**
- Can add **Figma links** to tasks and updates
- Focus on design-related tasks

### BDE
- **Full access** to leads/CRM
- Can create proposals and log meetings
- **Read-only** project overview (cannot see internals)
- Can recommend projects to CEO
- Can apply for leaves and view own attendance

## Usage Examples

### In Python Views
```python
from accounts.utils import has_permission, permission_required

# Decorator approach
@permission_required('projects', 'create')
def create_project_view(request):
    # Only users with permission can access
    pass

# Inline check
if has_permission(request.user, 'tasks', 'assign_anyone'):
    # Can assign to anyone
    assign_to = all_users
else:
    # Can only assign to Dev/UIUX
    assign_to = dev_uiux_users
```

### In Templates
```django
{% load permission_tags %}

{% if user|can_access:"projects:create" %}
    <a href="{% url 'projects:create' %}">Create Project</a>
{% endif %}

{% user_can user "tasks" "assign_anyone" as can_assign_anyone %}
{% if can_assign_anyone %}
    <!-- Show assign to anyone option -->
{% else %}
    <!-- Show only Dev/UIUX options -->
{% endif %}
```

## Setup Commands

```bash
# Create all roles with permissions
python manage.py setup_roles

# View all permissions
python manage.py show_permissions
```
