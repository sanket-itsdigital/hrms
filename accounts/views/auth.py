from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    Custom logout view that handles both GET and POST requests and redirects to login.
    """
    logout(request)
    return redirect('accounts:login')
