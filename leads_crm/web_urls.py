from django.urls import path
from leads_crm.views.web import (
    list_leads,
    create_lead,
    update_lead,
    convert_to_project,
    import_leads,
)

app_name = "leads_crm"

urlpatterns = [
    path("", list_leads, name="list"),
    path("create/", create_lead, name="create"),
    path("<int:id>/", update_lead, name="update"),
    path("<int:id>/convert/", convert_to_project, name="convert"),
    path("import/", import_leads, name="import"),
]
