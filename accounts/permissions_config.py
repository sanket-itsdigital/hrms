"""
Role-based permissions configuration for HRMS.
Defines what each role can do in the system.
"""

# Permission categories
PERMISSIONS = {
    'CEO': {
        'users': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'assign_role': True,
            'view_all': True,
        },
        'projects': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'assign_team': True,
            'view_all': True,
            'change_status': True,
            'view_budget': True,
        },
        'tasks': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'assign_anyone': True,
            'view_all': True,
            'change_status': True,
        },
        'attendance': {
            'create': False,
            'read': True,
            'update': False,
            'delete': False,
            'view_all': True,
            'view_reports': True,
        },
        'leaves': {
            'create': False,
            'read': True,
            'update': False,
            'delete': False,
            'approve': False,
            'reject': False,
            'view_all': True,
            'view_calendar': True,
        },
        'payroll': {
            'create': False,
            'read': True,
            'update': True,  # CEO can override if necessary
            'delete': False,
            'view_all': True,
            'view_summary': True,
            'generate_payslip': False,
        },
        'daily_updates': {
            'create': False,
            'read': True,
            'update': False,
            'delete': False,
            'view_all': True,
            'view_timeline': True,
        },
        'leads': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'view_all': True,
            'convert_to_project': True,
            'view_reports': True,
        },
        'reports': {
            'generate': True,
            'view_all': True,
            'export_pdf': True,
            'export_csv': True,
        },
        'notifications': {
            'create': True,
            'read': True,
            'view_all': True,
        },
        'audit_logs': {
            'view_all': True,
        },
    },
    
    'HR': {
        'users': {
            'create': False,
            'read': True,
            'update': False,  # Can update employee info but not roles
            'delete': False,
            'assign_role': False,
            'view_all': True,
            'view_profiles': True,
        },
        'projects': {
            'create': False,
            'read': True,  # Limited - only for context
            'update': False,
            'delete': False,
            'assign_team': False,
            'view_all': True,
            'change_status': False,
            'view_budget': False,
        },
        'tasks': {
            'create': False,
            'read': False,  # No access to project internals
            'update': False,
            'delete': False,
            'assign_anyone': False,
            'view_all': False,
            'change_status': False,
        },
        'attendance': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'view_all': True,
            'mark_attendance': True,
            'view_reports': True,
            'export_reports': True,
        },
        'leaves': {
            'create': False,
            'read': True,
            'update': False,
            'delete': False,
            'approve': True,
            'reject': True,
            'view_all': True,
            'view_calendar': True,
            'manage_balances': True,
        },
        'payroll': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'view_all': True,
            'calculate_salary': True,
            'generate_payslip': True,
            'export_reports': True,
        },
        'daily_updates': {
            'create': False,
            'read': False,  # No access
            'update': False,
            'delete': False,
            'view_all': False,
        },
        'leads': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_all': False,
        },
        'reports': {
            'generate': True,
            'view_all': True,
            'export_pdf': True,
            'export_csv': True,
            'attendance_reports': True,
            'payroll_reports': True,
            'leave_reports': True,
        },
        'notifications': {
            'create': True,
            'read': True,
            'view_all': True,
        },
        'audit_logs': {
            'view_all': True,
            'view_attendance_logs': True,
            'view_payroll_logs': True,
            'view_leave_logs': True,
        },
    },
    
    'PM': {
        'users': {
            'create': False,
            'read': True,  # Only team members
            'update': False,
            'delete': False,
            'assign_role': False,
            'view_all': False,
            'view_team': True,
        },
        'projects': {
            'create': False,
            'read': True,
            'update': True,  # Only assigned projects
            'delete': False,
            'assign_team': True,  # Can assign Dev/UIUX to assigned projects
            'view_all': False,
            'view_assigned': True,
            'change_status': True,
            'view_budget': True,
        },
        'tasks': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'assign_anyone': False,  # Can only assign Dev/UIUX
            'assign_dev_uiux': True,
            'view_all': False,
            'view_project_tasks': True,
            'change_status': True,
        },
        'attendance': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_all': False,
        },
        'leaves': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'approve': False,
            'reject': False,
            'view_all': False,
        },
        'payroll': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_all': False,
        },
        'daily_updates': {
            'create': False,
            'read': True,  # Can view updates for assigned projects
            'update': False,
            'delete': False,
            'view_all': False,
            'view_project_updates': True,
        },
        'leads': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_all': False,
        },
        'reports': {
            'generate': False,
            'view_all': False,
            'view_project_reports': True,
        },
        'notifications': {
            'create': True,
            'read': True,
            'view_all': False,
        },
        'audit_logs': {
            'view_all': False,
            'view_project_logs': True,
        },
    },
    
    'DEV': {
        'users': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'projects': {
            'create': False,
            'read': True,  # Read-only access to all projects
            'update': False,
            'delete': False,
            'view_all': True,
            'view_assigned': True,
        },
        'tasks': {
            'create': False,
            'read': True,
            'update': True,  # Can update own tasks
            'delete': False,
            'view_all': False,
            'view_assigned': True,
            'change_status': True,  # Can change status of assigned tasks
        },
        'attendance': {
            'create': False,
            'read': True,  # Own attendance only
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'leaves': {
            'create': True,
            'read': True,  # Own leaves only
            'update': True,  # Can update pending leaves
            'delete': True,  # Can delete pending leaves
            'approve': False,
            'reject': False,
            'view_own': True,
        },
        'payroll': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': False,
        },
        'daily_updates': {
            'create': True,
            'read': True,  # Own updates
            'update': True,  # Can update own updates
            'delete': True,  # Can delete own updates
            'view_own': True,
            'view_project_updates': True,  # Can view updates for assigned projects
        },
        'leads': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
        },
        'reports': {
            'generate': False,
            'view_all': False,
        },
        'notifications': {
            'create': False,
            'read': True,
            'view_own': True,
        },
        'audit_logs': {
            'view_all': False,
        },
    },
    
    'UIUX': {
        'users': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'projects': {
            'create': False,
            'read': True,  # Read-only access to all projects
            'update': False,
            'delete': False,
            'view_all': True,
            'view_assigned': True,
        },
        'tasks': {
            'create': False,
            'read': True,
            'update': True,  # Can update own design tasks
            'delete': False,
            'view_all': False,
            'view_assigned': True,
            'change_status': True,
            'upload_assets': True,
            'add_figma_links': True,
        },
        'attendance': {
            'create': False,
            'read': True,  # Own attendance only
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'leaves': {
            'create': True,
            'read': True,  # Own leaves only
            'update': True,
            'delete': True,
            'approve': False,
            'reject': False,
            'view_own': True,
        },
        'payroll': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': False,
        },
        'daily_updates': {
            'create': True,
            'read': True,  # Own updates
            'update': True,
            'delete': True,
            'view_own': True,
            'view_project_updates': True,
            'upload_assets': True,
            'add_figma_links': True,
        },
        'leads': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
        },
        'reports': {
            'generate': False,
            'view_all': False,
        },
        'notifications': {
            'create': False,
            'read': True,
            'view_own': True,
        },
        'audit_logs': {
            'view_all': False,
        },
    },
    
    'BDE': {
        'users': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'projects': {
            'create': False,
            'read': True,  # Read-only overview
            'update': False,
            'delete': False,
            'view_all': True,
            'view_overview': True,
            'recommend_projects': True,
        },
        'tasks': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
        },
        'attendance': {
            'create': False,
            'read': True,  # Own attendance only
            'update': False,
            'delete': False,
            'view_own': True,
        },
        'leaves': {
            'create': True,
            'read': True,  # Own leaves only
            'update': True,
            'delete': True,
            'approve': False,
            'reject': False,
            'view_own': True,
        },
        'payroll': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
            'view_own': False,
        },
        'daily_updates': {
            'create': False,
            'read': False,
            'update': False,
            'delete': False,
        },
        'leads': {
            'create': True,
            'read': True,
            'update': True,
            'delete': True,
            'view_all': True,
            'manage_pipeline': True,
            'create_proposals': True,
            'log_meetings': True,
            'convert_to_project': False,  # Can recommend, CEO converts
        },
        'reports': {
            'generate': False,
            'view_all': False,
            'view_lead_reports': True,
            'view_conversion_reports': True,
        },
        'notifications': {
            'create': False,
            'read': True,
            'view_own': True,
        },
        'audit_logs': {
            'view_all': False,
            'view_lead_logs': True,
        },
    },
}


def get_role_permissions(role_name):
    """
    Get permissions for a specific role.
    Returns empty dict if role not found.
    """
    return PERMISSIONS.get(role_name, {})


def has_permission(role_name, module, action):
    """
    Check if a role has a specific permission.
    
    Args:
        role_name: Role name (CEO, HR, PM, DEV, UIUX, BDE)
        module: Module name (users, projects, tasks, etc.)
        action: Action name (create, read, update, delete, etc.)
    
    Returns:
        bool: True if role has permission, False otherwise
    """
    if role_name == 'CEO':
        return True  # CEO has all permissions
    
    role_perms = PERMISSIONS.get(role_name, {})
    module_perms = role_perms.get(module, {})
    return module_perms.get(action, False)


def get_all_permissions():
    """
    Get all permissions configuration.
    """
    return PERMISSIONS


def get_module_permissions(role_name, module):
    """
    Get all permissions for a specific module and role.
    """
    role_perms = PERMISSIONS.get(role_name, {})
    return role_perms.get(module, {})
