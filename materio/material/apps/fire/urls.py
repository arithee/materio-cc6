from django.urls import path
from .views import DashboardsView, MultilineIncidentTop3Country, multipleBarbySeverity



urlpatterns = [
    path("", DashboardsView.as_view(template_name="dashboard_analytics.html"), name="index",), 
    path('multilineChart/', MultilineIncidentTop3Country, name='chart'),
    path('multiBarChart/', multipleBarbySeverity, name='chart'),
]
