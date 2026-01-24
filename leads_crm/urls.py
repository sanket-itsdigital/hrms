from django.urls import path, include
from rest_framework.routers import DefaultRouter
from leads_crm.views import LeadViewSet
from leads_crm.views.web import list_leads, create_lead, update_lead, convert_to_project

app_name = "leads_crm"

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

urlpatterns = [
    # Web routes (prefixed with /web/)
    path("web/", list_leads, name="list"),
    path("web/create/", create_lead, name="create"),
    path("web/<int:id>/", update_lead, name="update"),
    path("web/<int:id>/convert/", convert_to_project, name="convert"),
    # API routes (/api/leads/)
    path("", include(router.urls)),
]
