# HRMS Role Permissions - Sample Data & Examples

This document shows sample permission data structures and usage examples for all roles.

---

## Sample Permission Data Structure

### CEO Role Permissions Sample

```json
{
  "users": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "assign_role": true,
    "view_all": true
  },
  "projects": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "assign_team": true,
    "view_all": true,
    "change_status": true,
    "view_budget": true
  },
  "tasks": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "assign_anyone": true,
    "view_all": true,
    "change_status": true
  },
  "attendance": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": true,
    "view_reports": true
  },
  "leaves": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "approve": false,
    "reject": false,
    "view_all": true,
    "view_calendar": true
  },
  "payroll": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "view_all": true,
    "view_summary": true,
    "generate_payslip": false
  },
  "daily_updates": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": true,
    "view_timeline": true
  },
  "leads": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_all": true,
    "convert_to_project": true,
    "view_reports": true
  },
  "reports": {
    "generate": true,
    "view_all": true,
    "export_pdf": true,
    "export_csv": true
  },
  "notifications": {
    "create": true,
    "read": true,
    "view_all": true
  },
  "audit_logs": {
    "view_all": true
  }
}
```

---

### HR Role Permissions Sample

```json
{
  "users": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "assign_role": false,
    "view_all": true,
    "view_profiles": true
  },
  "projects": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "assign_team": false,
    "view_all": true,
    "change_status": false,
    "view_budget": false
  },
  "tasks": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "assign_anyone": false,
    "view_all": false,
    "change_status": false
  },
  "attendance": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_all": true,
    "mark_attendance": true,
    "view_reports": true,
    "export_reports": true
  },
  "leaves": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "approve": true,
    "reject": true,
    "view_all": true,
    "view_calendar": true,
    "manage_balances": true
  },
  "payroll": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_all": true,
    "calculate_salary": true,
    "generate_payslip": true,
    "export_reports": true
  },
  "daily_updates": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_all": false
  },
  "leads": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_all": false
  },
  "reports": {
    "generate": true,
    "view_all": true,
    "export_pdf": true,
    "export_csv": true,
    "attendance_reports": true,
    "payroll_reports": true,
    "leave_reports": true
  },
  "notifications": {
    "create": true,
    "read": true,
    "view_all": true
  },
  "audit_logs": {
    "view_all": true,
    "view_attendance_logs": true,
    "view_payroll_logs": true,
    "view_leave_logs": true
  }
}
```

---

### PM (Project Manager) Role Permissions Sample

```json
{
  "users": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "assign_role": false,
    "view_all": false,
    "view_team": true
  },
  "projects": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "assign_team": true,
    "view_all": false,
    "view_assigned": true,
    "change_status": true,
    "view_budget": true
  },
  "tasks": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "assign_anyone": false,
    "assign_dev_uiux": true,
    "view_all": false,
    "view_project_tasks": true,
    "change_status": true
  },
  "attendance": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_all": false
  },
  "leaves": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "approve": false,
    "reject": false,
    "view_all": false
  },
  "payroll": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_all": false
  },
  "daily_updates": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": false,
    "view_project_updates": true
  },
  "leads": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_all": false
  },
  "reports": {
    "generate": false,
    "view_all": false,
    "view_project_reports": true
  },
  "notifications": {
    "create": true,
    "read": true,
    "view_all": false
  },
  "audit_logs": {
    "view_all": false,
    "view_project_logs": true
  }
}
```

---

### DEV (Developer) Role Permissions Sample

```json
{
  "users": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "projects": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": true,
    "view_assigned": true
  },
  "tasks": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "view_all": false,
    "view_assigned": true,
    "change_status": true
  },
  "attendance": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "leaves": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "approve": false,
    "reject": false,
    "view_own": true
  },
  "payroll": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": false
  },
  "daily_updates": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_own": true,
    "view_project_updates": true
  },
  "leads": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false
  },
  "reports": {
    "generate": false,
    "view_all": false
  },
  "notifications": {
    "create": false,
    "read": true,
    "view_own": true
  },
  "audit_logs": {
    "view_all": false
  }
}
```

---

### UIUX (UI/UX Designer) Role Permissions Sample

```json
{
  "users": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "projects": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": true,
    "view_assigned": true
  },
  "tasks": {
    "create": false,
    "read": true,
    "update": true,
    "delete": false,
    "view_all": false,
    "view_assigned": true,
    "change_status": true,
    "upload_assets": true,
    "add_figma_links": true
  },
  "attendance": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "leaves": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "approve": false,
    "reject": false,
    "view_own": true
  },
  "payroll": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": false
  },
  "daily_updates": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_own": true,
    "view_project_updates": true,
    "upload_assets": true,
    "add_figma_links": true
  },
  "leads": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false
  },
  "reports": {
    "generate": false,
    "view_all": false
  },
  "notifications": {
    "create": false,
    "read": true,
    "view_own": true
  },
  "audit_logs": {
    "view_all": false
  }
}
```

---

### BDE (Business Development Executive) Role Permissions Sample

```json
{
  "users": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "projects": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_all": true,
    "view_overview": true,
    "recommend_projects": true
  },
  "tasks": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false
  },
  "attendance": {
    "create": false,
    "read": true,
    "update": false,
    "delete": false,
    "view_own": true
  },
  "leaves": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "approve": false,
    "reject": false,
    "view_own": true
  },
  "payroll": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false,
    "view_own": false
  },
  "daily_updates": {
    "create": false,
    "read": false,
    "update": false,
    "delete": false
  },
  "leads": {
    "create": true,
    "read": true,
    "update": true,
    "delete": true,
    "view_all": true,
    "manage_pipeline": true,
    "create_proposals": true,
    "log_meetings": true,
    "convert_to_project": false
  },
  "reports": {
    "generate": false,
    "view_all": false,
    "view_lead_reports": true,
    "view_conversion_reports": true
  },
  "notifications": {
    "create": false,
    "read": true,
    "view_own": true
  },
  "audit_logs": {
    "view_all": false,
    "view_lead_logs": true
  }
}
```

---

## Code Examples - Permission Checks

### Example 1: View with Permission Decorator

```python
# projects/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.utils import permission_required, has_permission
from projects.models import Project

@permission_required('projects', 'create')
def create_project(request):
    """Only users with project create permission can access"""
    if request.method == 'POST':
        # Create project logic
        pass
    return render(request, 'projects/create.html')

@permission_required('projects', 'read')
def project_list(request):
    """View projects based on permission"""
    user = request.user
    
    if has_permission(user, 'projects', 'view_all'):
        # CEO, HR can see all projects
        projects = Project.objects.all()
    elif has_permission(user, 'projects', 'view_assigned'):
        # PM, DEV, UIUX see assigned projects
        projects = Project.objects.filter(
            assignments__user=user
        ).distinct()
    else:
        # BDE sees overview only
        projects = Project.objects.all()[:10]  # Limited view
    
    return render(request, 'projects/list.html', {'projects': projects})
```

---

### Example 2: Task Assignment Logic

```python
# tasks/views.py
from accounts.utils import has_permission
from accounts.models import User

def assign_task(request, task_id):
    """Assign task with permission check"""
    task = Task.objects.get(id=task_id)
    user = request.user
    
    # Check if user can assign tasks
    if not has_permission(user, 'tasks', 'create'):
        messages.error(request, 'You cannot assign tasks.')
        return redirect('tasks:list')
    
    # Get assignable users based on permission
    if has_permission(user, 'tasks', 'assign_anyone'):
        # CEO can assign to anyone
        assignable_users = User.objects.filter(
            organization=user.organization
        )
    elif has_permission(user, 'tasks', 'assign_dev_uiux'):
        # PM can only assign to Dev/UIUX
        assignable_users = User.objects.filter(
            organization=user.organization,
            role__name__in=['DEV', 'UIUX']
        )
    else:
        messages.error(request, 'You cannot assign tasks.')
        return redirect('tasks:list')
    
    if request.method == 'POST':
        assigned_user_id = request.POST.get('assigned_to')
        task.assigned_to_id = assigned_user_id
        task.save()
        messages.success(request, 'Task assigned successfully.')
        return redirect('tasks:detail', task_id=task.id)
    
    return render(request, 'tasks/assign.html', {
        'task': task,
        'assignable_users': assignable_users
    })
```

---

### Example 3: Attendance Management

```python
# attendance/views.py
from accounts.utils import has_permission, permission_required

@permission_required('attendance', 'read')
def attendance_list(request):
    """View attendance based on permission"""
    user = request.user
    
    if has_permission(user, 'attendance', 'view_all'):
        # CEO, HR can see all attendance
        attendance_records = Attendance.objects.filter(
            organization=user.organization
        )
    elif has_permission(user, 'attendance', 'view_own'):
        # Employees see only their own
        attendance_records = Attendance.objects.filter(
            user=user
        )
    else:
        messages.error(request, 'You do not have permission to view attendance.')
        return redirect('accounts:dashboard')
    
    return render(request, 'attendance/list.html', {
        'attendance_records': attendance_records
    })

@permission_required('attendance', 'create')
def mark_attendance(request):
    """Only HR can mark attendance"""
    if request.method == 'POST':
        # Mark attendance logic
        pass
    return render(request, 'attendance/mark.html')
```

---

### Example 4: Leave Approval

```python
# leaves/views.py
from accounts.utils import has_permission

def leave_list(request):
    """View leaves based on permission"""
    user = request.user
    
    if has_permission(user, 'leaves', 'view_all'):
        # CEO, HR can see all leaves
        leaves = Leave.objects.filter(
            user__organization=user.organization
        )
    elif has_permission(user, 'leaves', 'view_own'):
        # Employees see only their own
        leaves = Leave.objects.filter(user=user)
    else:
        messages.error(request, 'You do not have permission to view leaves.')
        return redirect('accounts:dashboard')
    
    return render(request, 'leaves/list.html', {'leaves': leaves})

@permission_required('leaves', 'approve')
def approve_leave(request, leave_id):
    """Only HR can approve leaves"""
    leave = Leave.objects.get(id=leave_id)
    
    if request.method == 'POST':
        leave.status = 'APPROVED'
        leave.approved_by = request.user
        leave.save()
        messages.success(request, 'Leave approved successfully.')
        return redirect('leaves:list')
    
    return render(request, 'leaves/approve.html', {'leave': leave})
```

---

### Example 5: Payroll Access

```python
# payroll/views.py
from accounts.utils import has_permission

def payroll_list(request):
    """View payroll based on permission"""
    user = request.user
    
    if has_permission(user, 'payroll', 'view_all'):
        # CEO, HR can see all payroll
        payroll_records = Payroll.objects.filter(
            employee__organization=user.organization
        )
    elif has_permission(user, 'payroll', 'view_own'):
        # Employees see only their own (if allowed)
        payroll_records = Payroll.objects.filter(employee=user)
    else:
        messages.error(request, 'You do not have permission to view payroll.')
        return redirect('accounts:dashboard')
    
    return render(request, 'payroll/list.html', {
        'payroll_records': payroll_records
    })

@permission_required('payroll', 'generate_payslip')
def generate_payslip(request, payroll_id):
    """Only HR can generate payslips"""
    payroll = Payroll.objects.get(id=payroll_id)
    # Generate PDF payslip
    return render(request, 'payroll/payslip.html', {'payroll': payroll})
```

---

### Example 6: Leads Management (BDE)

```python
# leads_crm/views.py
from accounts.utils import has_permission, permission_required

@permission_required('leads', 'read')
def leads_list(request):
    """View leads - BDE sees all, others see none"""
    user = request.user
    
    if has_permission(user, 'leads', 'view_all'):
        leads = Lead.objects.filter(organization=user.organization)
    else:
        messages.error(request, 'You do not have permission to view leads.')
        return redirect('accounts:dashboard')
    
    return render(request, 'leads/list.html', {'leads': leads})

@permission_required('leads', 'create')
def create_lead(request):
    """Only BDE and CEO can create leads"""
    if request.method == 'POST':
        # Create lead logic
        pass
    return render(request, 'leads/create.html')

@permission_required('leads', 'convert_to_project')
def convert_to_project(request, lead_id):
    """Only CEO can convert lead to project"""
    lead = Lead.objects.get(id=lead_id)
    # Convert logic
    return redirect('projects:create')
```

---

## Template Examples

### Example 1: Show/Hide Buttons Based on Permission

```django
<!-- projects/list.html -->
{% load permission_tags %}

<div class="flex gap-2">
    {% if user|can_access:"projects:create" %}
        <a href="{% url 'projects:create' %}" class="btn btn-primary">
            Create Project
        </a>
    {% endif %}
    
    {% if user|can_access:"projects:update" %}
        <a href="{% url 'projects:edit' project.id %}" class="btn btn-secondary">
            Edit
        </a>
    {% endif %}
    
    {% if user|can_access:"projects:delete" %}
        <a href="{% url 'projects:delete' project.id %}" class="btn btn-error">
            Delete
        </a>
    {% endif %}
</div>
```

---

### Example 2: Conditional Task Assignment

```django
<!-- tasks/assign.html -->
{% load permission_tags %}

{% user_can user "tasks" "assign_anyone" as can_assign_anyone %}
{% user_can user "tasks" "assign_dev_uiux" as can_assign_dev_uiux %}

{% if can_assign_anyone or can_assign_dev_uiux %}
    <form method="post">
        <select name="assigned_to" class="select select-bordered">
            {% if can_assign_anyone %}
                <option value="">All Employees</option>
                {% for emp in all_employees %}
                    <option value="{{ emp.id }}">{{ emp.get_full_name }}</option>
                {% endfor %}
            {% elif can_assign_dev_uiux %}
                <option value="">Dev/UIUX Only</option>
                {% for emp in dev_uiux_employees %}
                    <option value="{{ emp.id }}">{{ emp.get_full_name }}</option>
                {% endfor %}
            {% endif %}
        </select>
        <button type="submit" class="btn btn-primary">Assign</button>
    </form>
{% else %}
    <p class="text-error">You do not have permission to assign tasks.</p>
{% endif %}
```

---

### Example 3: Role-Based Menu Items

```django
<!-- includes/sidebar.html -->
{% load permission_tags %}

<ul class="menu">
    <li>
        <a href="{% url 'accounts:dashboard' %}">Dashboard</a>
    </li>
    
    {% if user|can_access:"projects:read" %}
        <li>
            <a href="{% url 'projects:list' %}">Projects</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"tasks:read" %}
        <li>
            <a href="{% url 'tasks:list' %}">Tasks</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"attendance:read" %}
        <li>
            <a href="{% url 'attendance:list' %}">Attendance</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"leaves:read" %}
        <li>
            <a href="{% url 'leaves:list' %}">Leaves</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"payroll:read" %}
        <li>
            <a href="{% url 'payroll:list' %}">Payroll</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"leads:read" %}
        <li>
            <a href="{% url 'leads:list' %}">Leads</a>
        </li>
    {% endif %}
    
    {% if user|can_access:"reports:generate" %}
        <li>
            <a href="{% url 'reports:list' %}">Reports</a>
        </li>
    {% endif %}
</ul>
```

---

### Example 4: Conditional Fields in Forms

```django
<!-- projects/form.html -->
{% load permission_tags %}

<form method="post">
    {% csrf_token %}
    
    {{ form.name }}
    {{ form.description }}
    {{ form.deadline }}
    
    {% if user|can_access:"projects:view_budget" %}
        {{ form.budget }}
        {{ form.payment_details }}
    {% endif %}
    
    {% if user|can_access:"projects:assign_team" %}
        <div class="form-control">
            <label>Assign Project Manager</label>
            {{ form.project_manager }}
        </div>
        <div class="form-control">
            <label>Assign Team Members</label>
            {{ form.team_members }}
        </div>
    {% endif %}
    
    <button type="submit" class="btn btn-primary">Save</button>
</form>
```

---

## API/DRF Permission Examples

```python
# projects/permissions.py
from rest_framework import permissions
from accounts.utils import has_permission

class ProjectPermission(permissions.BasePermission):
    """Custom permission for projects"""
    
    def has_permission(self, request, view):
        if view.action == 'create':
            return has_permission(request.user, 'projects', 'create')
        elif view.action in ['list', 'retrieve']:
            return has_permission(request.user, 'projects', 'read')
        elif view.action in ['update', 'partial_update']:
            return has_permission(request.user, 'projects', 'update')
        elif view.action == 'destroy':
            return has_permission(request.user, 'projects', 'delete')
        return False
    
    def has_object_permission(self, request, view, obj):
        """Check object-level permissions"""
        user = request.user
        
        # CEO can access all
        if has_permission(user, 'projects', 'view_all'):
            return True
        
        # PM can only access assigned projects
        if has_permission(user, 'projects', 'view_assigned'):
            return obj.assignments.filter(user=user).exists()
        
        return False
```

---

## Testing Permission Examples

```python
# tests/test_permissions.py
from django.test import TestCase
from accounts.models import User, Role, Organization
from accounts.utils import has_permission

class PermissionTestCase(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="Test Org")
        self.ceo_role = Role.objects.get(name='CEO')
        self.hr_role = Role.objects.get(name='HR')
        self.dev_role = Role.objects.get(name='DEV')
        
        self.ceo = User.objects.create_user(
            username='ceo',
            email='ceo@test.com',
            role=self.ceo_role,
            organization=self.org
        )
        
        self.hr = User.objects.create_user(
            username='hr',
            email='hr@test.com',
            role=self.hr_role,
            organization=self.org
        )
        
        self.dev = User.objects.create_user(
            username='dev',
            email='dev@test.com',
            role=self.dev_role,
            organization=self.org
        )
    
    def test_ceo_has_all_permissions(self):
        """CEO should have all permissions"""
        self.assertTrue(has_permission(self.ceo, 'projects', 'create'))
        self.assertTrue(has_permission(self.ceo, 'tasks', 'create'))
        self.assertTrue(has_permission(self.ceo, 'users', 'create'))
    
    def test_hr_can_manage_attendance(self):
        """HR should manage attendance"""
        self.assertTrue(has_permission(self.hr, 'attendance', 'create'))
        self.assertTrue(has_permission(self.hr, 'attendance', 'update'))
        self.assertFalse(has_permission(self.hr, 'tasks', 'create'))
    
    def test_dev_can_submit_updates(self):
        """Developer should submit daily updates"""
        self.assertTrue(has_permission(self.dev, 'daily_updates', 'create'))
        self.assertFalse(has_permission(self.dev, 'projects', 'create'))
        self.assertFalse(has_permission(self.dev, 'attendance', 'create'))
```

---

## Quick Permission Check Reference

```python
# Quick checks for common scenarios

# Can user create projects?
has_permission(user, 'projects', 'create')  # CEO only

# Can user assign tasks to anyone?
has_permission(user, 'tasks', 'assign_anyone')  # CEO only

# Can user mark attendance?
has_permission(user, 'attendance', 'create')  # HR only

# Can user approve leaves?
has_permission(user, 'leaves', 'approve')  # HR only

# Can user generate payslips?
has_permission(user, 'payroll', 'generate_payslip')  # HR only

# Can user view all projects?
has_permission(user, 'projects', 'view_all')  # CEO, HR, DEV, UIUX, BDE (read-only)

# Can user manage leads?
has_permission(user, 'leads', 'create')  # CEO, BDE

# Can user upload design assets?
has_permission(user, 'tasks', 'upload_assets')  # UIUX only
```

---

This document provides complete sample permission data and usage examples for all roles in the HRMS system.
