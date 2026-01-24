from django.urls import include, path
from rest_framework.routers import DefaultRouter
from leads_crm.views import LeadViewSet

app_name = "leads_crm_api"

router = DefaultRouter()
router.register(r"", LeadViewSet, basename="lead")

urlpatterns = [
    path("", include(router.urls)),
]
