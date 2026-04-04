import json
import pandas as pd

## Procesare fisier cu Spitale din Romania -> Luam doar numele, orasul, latitudinea si longitudinea


with open('data\spitale_Romania.geojson', encoding='utf-8') as f:
    data = json.load(f)


hospitals_list = []

for feature in data['features']:
    props = feature.get('properties', {})
    geom = feature.get('geometry', {})
    
    
    if geom['type'] == 'Point':
        long, lat = geom['coordinates']
    elif 'center' in feature:
        long, lat = feature['center']['lon'], feature['center']['lat']
    else:
        continue

    hospitals_list.append({
        'nume': props.get('name', 'N/A'),
        'oras': props.get('addr:city', props.get('is_in:city', 'Necunoscut')),
        'lat': lat,
        'long': long
    })


df = pd.DataFrame(hospitals_list)

# Eliminăm intrările care nu au nume
df = df[df['nume'] != 'N/A'].reset_index(drop=True)

#Eliminam si intrarile cu orase necunoscute
df = df[df['oras'] != 'Necunoscut'].reset_index(drop=True)

df['lat_round'] = df['lat'].round(4)
df['lon_round'] = df['long'].round(4)


# Eliminam si duplicatele in functie de long si lat, si numele (fara case sensitive)
df_unic = df.drop_duplicates(subset=['lat_round', 'lon_round'], keep='first')

df_unic = df_unic.drop(columns=['lat_round', 'lon_round'])

df_unic['nume_upper'] = df_unic['nume'].str.upper().str.strip()
df_unic = df_unic.drop_duplicates(subset=['nume_upper'], keep='first')
df_unic = df_unic.drop(columns=['nume_upper'])

print(f"Rămase după filtrare: {len(df_unic)} spitale unice.")



df_unic.to_csv('data\spitale.csv', index=False)
print(f"Am extras {len(df_unic)} spitale în 'spitale.csv'")