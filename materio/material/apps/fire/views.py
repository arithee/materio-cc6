from django.views.generic import TemplateView
from web_project import TemplateLayout
from .models import Firefighters, FireTruck, FireStation, Incident
from django.views.generic.list import ListView
from django.db import connection
from django.http import JsonResponse


"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardsView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['firefighters_count'] = Firefighters.objects.count()
        context['firetrucks_count'] = FireTruck.objects.count()
        context['firestations_count'] = FireStation.objects.count()
        context['incidents_count'] = Incident.objects.count()
        return context

def MultilineIncidentTop3Country(request):
    query = '''
    SELECT 
        fl.country, 
        strftime('%m', fi.date_time) AS month, 
        COUNT(fi.id) AS incident_count
    FROM 
        fire_incident fi
    JOIN 
        fire_locations fl ON fi.location_id = fl.id
    WHERE 
    fl.country IN (
        SELECT 
            fl_top.country
        FROM 
            fire_incident fi_top
        JOIN 
            fire_locations fl_top ON fi_top.location_id = fl_top.id
        WHERE 
            strftime('%Y', fi_top.date_time) = strftime('%Y', 'now')
        GROUP BY 
            fl_top.country
        ORDER BY 
            COUNT(fi_top.id) DESC
        LIMIT 3
    ) 
        AND strftime('%Y', fi.date_time) = strftime('%Y', 'now')
    GROUP BY 
        fl.country, month
    ORDER BY 
        fl.country, month;
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Initialize a dictionary to store the result
    result = {}

    # Initialize a set of months from January to December
    months = set(str(i).zfill(2) for i in range(1, 13))

    # Loop through the query results
    for row in rows:
        country = row[0]
        month = row[1]
        total_incidents = row[2]

        # If the country is not in the result dictionary, initialize it with all months set to zero
        if country not in result:
            result[country] = {month: 0 for month in months}

        # Update the incident count for the corresponding month
        result[country][month] = total_incidents

    # Ensure there are always 3 countries in the result
    while len(result) < 3:
        # Placeholder name for missing countries
        missing_country = f"Country {len(result) + 1}"
        result[missing_country] = {month: 0 for month in months}

    # Sort months for each country
    for country in result:
        result[country] = dict(sorted(result[country].items()))

    return JsonResponse(result)


def multipleBarbySeverity(request):
    query = '''
        SELECT
            fi.severity_level,
            strftime('%m', fi.date_time) AS month,
            COUNT(fi.id) AS incident_count
        FROM
            fire_incident fi
        GROUP BY fi.severity_level, month
        '''

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = {}
    months = set(str(i).zfill(2) for i in range(1, 13))

    for row in rows:
        level = str(row[0])  # Ensure the severity level is a string
        month = row[1]
        total_incidents = row[2]

        if level not in result:
            result[level] = {month: 0 for month in months}

        result[level][month] = total_incidents

    # Sort months within each severity level
    for level in result:
        result[level] = dict(sorted(result[level].items()))

    return JsonResponse(result)

def PieCountbySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    labels = []
    counts = []
    for severity, count in rows:
        labels.append(severity)
        counts.append(count)

    return JsonResponse({'labels': labels, 'counts': counts})

def LineCountFirestations(request):
    query = '''
    SELECT city, COUNT(*) as count
    FROM fire_firestation
    GROUP BY city
    ORDER BY city
    '''
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    data = {}
    for city, count in rows:
        data[city] = count

    return JsonResponse(data)