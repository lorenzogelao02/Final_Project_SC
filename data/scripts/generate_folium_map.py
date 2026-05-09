#!/usr/bin/env python3
"""
Generate an interactive folium map (final_survival_map.html) from processed CSVs.
Saves the HTML into the website/ folder so the site iframe can load it.
"""
import os
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / 'data' / 'processed'
OUT = ROOT / 'website' / 'final_survival_map.html'

def get_custom_cluster(color, glow_color, shape="50%"):
    return f"""
    function(cluster) {{
        return new L.DivIcon({{ 
            html: '<div style="background-color: {color}; color: white; border-radius: {shape}; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center; border: 2px solid {glow_color}; box-shadow: 0 0 12px {glow_color}; font-weight: bold;">' + cluster.getChildCount() + '</div>', 
            className: 'marker-cluster', iconSize: new L.Point(40, 40) 
        }});
    }}
    """

def load_csv(name):
    p = PROC / name
    if not p.exists():
        print(f"Warning: {p} not found")
        return pd.DataFrame()
    return pd.read_csv(p)

def main():
    import folium
    from folium import plugins

    fountains = load_csv('drinking_fountains_cleaned.csv')
    centers = load_csv('drop_in_centers_cleaned.csv')
    link = load_csv('link_nyc_cleaned.csv')
    toilets = load_csv('public_toilets_cleaned.csv')
    crime = load_csv('drug_crime_cleaned.csv')

    # Basic recent crime filter if date column exists
    if 'cmplnt_fr_dt' in crime.columns:
        crime['cmplnt_fr_dt'] = pd.to_datetime(crime['cmplnt_fr_dt'], errors='coerce')
        recent_crime = crime[crime['cmplnt_fr_dt'].dt.year >= 2014].copy()
    else:
        recent_crime = crime.copy()

    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11, tiles='CartoDB dark_matter')

    # CRIME HOTSPOTS
    if not recent_crime.empty and 'latitude' in recent_crime.columns and 'longitude' in recent_crime.columns:
        weights = recent_crime.groupby(['latitude', 'longitude']).size().reset_index(name='count')
        if not weights.empty:
            hotspots = weights[weights['count'] > weights['count'].quantile(0.95)]
            plugins.HeatMap(
                hotspots[['latitude','longitude','count']].values.tolist(),
                name='Crime Risk Hotspots', radius=10, blur=8, min_opacity=0.4,
                gradient={0.4: 'orange', 0.7: 'red', 1: 'darkred'}
            ).add_to(m)

    # RESOURCES
    # FOUNTAINS
    if not fountains.empty and 'latitude' in fountains.columns and 'longitude' in fountains.columns:
        fountain_cluster = plugins.MarkerCluster(name='Drinking Fountains', icon_create_function=get_custom_cluster('rgba(0, 191, 255, 0.7)','cyan')).add_to(m)
        for _, row in fountains.dropna(subset=['latitude','longitude']).iterrows():
            folium.CircleMarker(location=[row['latitude'], row['longitude']], radius=2.5, color='cyan', fill=True, fill_opacity=0.8, popup='Fountain').add_to(fountain_cluster)

    # LINKNYC
    if not link.empty and 'latitude' in link.columns and 'longitude' in link.columns:
        link_cluster = plugins.MarkerCluster(name='LinkNYC Wifi Hubs', icon_create_function=get_custom_cluster('rgba(30, 30, 30, 0.9)','gold','5px')).add_to(m)
        for _, row in link.dropna(subset=['latitude','longitude']).iterrows():
            try:
                folium.Marker(location=[row['latitude'], row['longitude']], icon=folium.Icon(color='black', icon='wifi', prefix='fa', icon_color='white'), popup='LinkNYC Hub').add_to(link_cluster)
            except Exception:
                folium.Marker(location=[row['latitude'], row['longitude']], popup='LinkNYC Hub').add_to(link_cluster)

    # CENTERS
    if not centers.empty and 'latitude' in centers.columns and 'longitude' in centers.columns:
        centers_layer = folium.FeatureGroup(name='Drop-in Centers')
        for _, row in centers.dropna(subset=['latitude','longitude']).iterrows():
            try:
                folium.Marker(location=[row['latitude'], row['longitude']], icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(centers_layer)
            except Exception:
                folium.Marker(location=[row['latitude'], row['longitude']]).add_to(centers_layer)
        centers_layer.add_to(m)

    # TOILETS
    if not toilets.empty and 'latitude' in toilets.columns and 'longitude' in toilets.columns:
        toilets_layer = folium.FeatureGroup(name='Public Toilets')
        for _, row in toilets.dropna(subset=['latitude','longitude']).iterrows():
            try:
                folium.Marker(location=[row['latitude'], row['longitude']], icon=folium.Icon(color='orange', icon='restroom', prefix='fa')).add_to(toilets_layer)
            except Exception:
                folium.Marker(location=[row['latitude'], row['longitude']]).add_to(toilets_layer)
        toilets_layer.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(OUT))
    print(f'Saved folium map to {OUT}')

if __name__ == '__main__':
    main()
