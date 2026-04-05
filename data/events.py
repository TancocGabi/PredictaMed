import os
import sys
import requests

base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

from data.data_class.eventsData import EventsData
from data.keys import Keys


#Trimite lista de evenimente
def get_romania_events(lat, lon, api_key, start_date="2026-04-01", end_date="2026-04-30"):
    url = "https://api.predicthq.com/v1/events/"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    params = {
        # 'within' combina distanta si punctul intr-un singur string validat
        "within": f"10km@{lat},{lon}", 
        "category": "festivals,sports,concerts",
        "active.gte": start_date,
        "active.lte": end_date,
        "rank.gte": 60,
        "phq_attendance.gte": 5000,
        "limit": 50
    }
    
    response = requests.get(url, headers=headers, params=params)


    if response.status_code == 200:
        raw_results = response.json().get('results', [])
        clean_events = []

        for event in raw_results:


            event_data = EventsData(
                titlu=event.get("title"),
                categorie=event.get("category"),
                data_start=event.get("start_local"),
                estimare_participanti=event.get("phq_attendance", 0),
                nivel_importanta=event.get("rank", 0),
                locatie_nume=event.get("geo", {}).get("address", {}).get("formatted_address", "N/A"),
                tip_detaliat=[label['label'] for label in event.get('phq_labels', [])]
            )
            clean_events.append(event_data)
        
        return clean_events
    else:
        print(f"Eroare: {response.status_code}, {response.text}")
        return []