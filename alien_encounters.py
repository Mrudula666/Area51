import csv
import re
import json
from collections import Counter

keywords = re.compile(r'\b(alien|entity|creature)s?\b', re.IGNORECASE)

subset = []
with open('ufo-sightings-transformed.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        desc = row['Description']
        if desc and keywords.search(desc):
            subset.append(row)

# write subset
with open('alien_encounters.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=subset[0].keys() if subset else [])
    if subset:
        writer.writeheader()
        writer.writerows(subset)

country_counts = Counter(row['Country'] for row in subset)

print(f'Total alien-related encounters: {len(subset)}')
print('Counts by country:')
for country, count in country_counts.most_common():
    print(f'  {country}: {count}')

points = []
for row in subset:
    lat = row['latitude']
    lon = row['longitude']
    if lat and lon:
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue
        popup = row['Description'][:100].replace("'", "&#39;").replace("\n", " ")
        points.append({'lat': lat, 'lon': lon, 'popup': popup})

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'/>
<title>Alien Encounters Map</title>
<link rel='stylesheet' href='https://unpkg.com/leaflet@1.9.3/dist/leaflet.css'/>
<script src='https://unpkg.com/leaflet@1.9.3/dist/leaflet.js'></script>
</head>
<body>
<div id='map' style='width:100%; height:600px;'></div>
<script>
var map = L.map('map').setView([20,0], 2);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  maxZoom: 18,
  attribution: '&copy; OpenStreetMap contributors'
}}).addTo(map);
var points = {json.dumps(points)};
points.forEach(function(p) {{
  L.marker([p.lat, p.lon]).addTo(map).bindPopup(p.popup);
}});
</script>
</body>
</html>
"""

with open('alien_encounters_map.html', 'w', encoding='utf-8') as f:
    f.write(html)
