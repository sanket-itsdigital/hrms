from django import forms
from django.db.models import Q
from .models import Attendance
from accounts.models import User
from organizations.models import Organization
from django.utils import timezone


class AttendanceForm(forms.ModelForm):
    """Form for creating and updating attendance records"""

    class Meta:
        model = Attendance
        fields = ["user", "date", "status", "check_in", "check_out", "notes"]
        widgets = {
            "user": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "date": forms.DateInput(
                attrs={"class": "input input-bordered w-full", "type": "date"}
            ),
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "check_in": forms.TimeInput(
                attrs={"class": "input input-bordered w-full", "type": "time"}
            ),
            "check_out": forms.TimeInput(
                attrs={"class": "input input-bordered w-full", "type": "time"}
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 3,
                    "placeholder": "Optional notes...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        # Filter users based on role and organization
        if user and organization:
            if user.is_ceo or user.is_hr:
                # CEO/HR can mark attendance for all employees (exclude CEO and superusers)
                self.fields["user"].queryset = (
                    User.objects.filter(organization=organization, is_active=True)
                    .exclude(role__name="CEO")
                    .exclude(is_superuser=True)
                    .order_by("first_name", "last_name")
                )
            else:
                # Others can only mark their own attendance
                self.fields["user"].queryset = User.objects.filter(id=user.id)
                self.fields["user"].widget.attrs["disabled"] = True

        # Set default date to today
        if not self.instance.pk:
            self.fields["date"].initial = timezone.now().date()

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        date = cleaned_data.get("date")

        # Check for duplicate attendance on same date
        if user and date:
            existing = Attendance.objects.filter(user=user, date=date)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError(
                    f"Attendance for {user.get_full_name()} on {date} already exists."
                )

        # Validate check-in and check-out times
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")

        if check_in and check_out and check_out <= check_in:
            raise forms.ValidationError("Check-out time must be after check-in time.")

        return cleaned_data


class AttendanceBulkForm(forms.Form):
    """Form for bulk attendance entry"""

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"class": "input input-bordered w-full", "type": "date"}
        )
    )
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox"}),
        required=True,
    )
    status = forms.ChoiceField(
        choices=Attendance.STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )
    check_in = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={"class": "input input-bordered w-full", "type": "time"}
        ),
    )
    check_out = forms.TimeField(
        required=False,
        widget=forms.TimeInput(
            attrs={"class": "input input-bordered w-full", "type": "time"}
        ),
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        organization = kwargs.pop("organization", None)
        super().__init__(*args, **kwargs)

        if user and organization and (user.is_ceo or user.is_hr):
            self.fields["users"].queryset = User.objects.filter(
                organization=organization, is_active=True
            ).order_by("first_name", "last_name")

        if not self.initial.get("date"):
            self.fields["date"].initial = timezone.now().date()
