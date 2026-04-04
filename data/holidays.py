import requests
from data_class.holidaysData import HolidaysData

def get_romania_holidays(year=2026):
    # API gratuit, nu necesita cheie
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/RO"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        holidays = response.json()
        clean_holidays = []
        for h in holidays:
            holiday = HolidaysData(
                nume=h['localName'],
                data=h['date'],
                tip="Sarbatoare Legala"
            )
            clean_holidays.append(holiday)
        return clean_holidays
    else:
        print(f"Eroare API Sarbatori: {response.status_code}")
        return []


# Exemplu de utilizare:
# sarbatori_2026 = get_romania_holidays(2026)
# print("Sărbători legale în România pentru 2026:")
# for sarbatoare in sarbatori_2026:
#     print(sarbatoare)