'''
Thinking of moving? Check if your desired location is near a Superfund site using this tool.

Disclaimer: Data may be outdated. Visit the EPA website for the latest info.
https://www.epa.gov/superfund/search-superfund-sites-where-you-live

This program requires lat/long coordinates. 
For mapping tools like Folium or Google Maps, 4–6 decimal places is ideal. 
More than 7 is rarely needed unless you're doing high-precision GPS work.
'''

import folium
from folium import Marker, Circle
import pandas as pd

# Superfund data
data = {
    'Latitude': [43.0935, 43.2736, 43.0848, 40.6736, 40.7365, 40.6997, 42.9414, 42.6333],
    'Longitude': [-79.0009, -73.5839, -76.211, -73.9903, -73.938, -73.9065, -78.7306, -73.5472], 
    'Superfund Status': ['Yes'] * 8,
    'Site Name': [
        'Love Canal', 'Hudson River PCBs', 'Onondaga Lake', 'Gowanus Canal', 
        'Newtown Creek', 'Wolff-Alport Chemical Company', 'Pfohl Brothers Landfill',
        'Dewey Loeffel Landfill'
    ],
    'County': [
        'Niagara', 'Washington', 'Onondaga', 'Kings (Brooklyn)',
        'Kings/Queens', 'Queens', 'Erie', 'Rensselaer'
    ]
}

df = pd.DataFrame(data)

# Ask user if they want to add a new site or skip
print("If you'd like to add a new site for comparison, enter the details below.")
print("Otherwise, press Enter to skip.")

user_input = input("Enter County,Latitude,Longitude,Superfund Status (Yes/No),Site Name or press Enter to skip: ").strip()

if user_input:
    try:
        county, lat, lon, status, site_name = [x.strip() for x in user_input.split(',')]
        new_site = {
            'Latitude': float(lat),
            'Longitude': float(lon),
            'Superfund Status': status,
            'Site Name': site_name,
            'County': county
        }
        df = pd.concat([df, pd.DataFrame([new_site])], ignore_index=True)
        print(f"Successfully added: {site_name} in {county}.")
    except Exception as e:
        print("Invalid input format. Skipping new site addition.")
        print("Error:", e)

# Create map centered on NY State
m = folium.Map(location=[42.9, -75], zoom_start=7)

# Add site markers and radius circles
for _, row in df.iterrows():
    location = [row['Latitude'], row['Longitude']]
    is_superfund = row['Superfund Status'].lower() == 'yes'
    color = 'red' if is_superfund else 'green'

    # Add marker
    Marker(
        location=location,
        popup=f"{row['Site Name']} ({row['County']})",
        icon=folium.Icon(color=color)
    ).add_to(m)

    # Add radius circle for all entries
    Circle(
        location=location,
        radius=1000,  # 1 km radius around Superfund site
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.2,
        popup=f"2 km radius around {row['Site Name']}"
    ).add_to(m)

# Show map
m

# Example Input:
# Queens,40.7650, -73.9304,No,Queens Example
