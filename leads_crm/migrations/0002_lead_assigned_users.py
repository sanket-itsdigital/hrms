from django.conf import settings
from django.db import migrations, models


def copy_primary_assignee(apps, schema_editor):
    Lead = apps.get_model("leads_crm", "Lead")
    for lead in Lead.objects.exclude(assigned_to=None):
        lead.assigned_users.add(lead.assigned_to)


class Migration(migrations.Migration):

    dependencies = [
        ("leads_crm", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="assigned_users",
            field=models.ManyToManyField(
                blank=True, related_name="lead_assignments", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.RunPython(copy_primary_assignee, migrations.RunPython.noop),
    ]
