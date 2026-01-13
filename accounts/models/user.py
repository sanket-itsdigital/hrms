from django.contrib.auth.models import AbstractUser
from django.db import models
from organizations.models import Organization


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports multi-organization and role-based access.
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profiles/', blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    role = models.ForeignKey(
        'accounts.Role',
        on_delete=models.SET_NULL,
        related_name='users',
        null=True,
        blank=True
    )
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    date_of_joining = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"

    @property
    def is_ceo(self):
        return self.role and self.role.name == 'CEO'

    @property
    def is_hr(self):
        return self.role and self.role.name == 'HR'

    @property
    def is_pm(self):
        return self.role and self.role.name == 'PM'

    @property
    def is_dev(self):
        return self.role and self.role.name == 'DEV'

    @property
    def is_uiux(self):
        return self.role and self.role.name == 'UIUX'

    @property
    def is_bde(self):
        return self.role and self.role.name == 'BDE'
