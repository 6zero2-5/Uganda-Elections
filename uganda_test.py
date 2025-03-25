import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen

# Load dataset
try:
    Election_df = pd.read_csv("Uganda_Election_Events.csv")
except FileNotFoundError:
    Election_df = pd.DataFrame(columns=["event_type", "latitude", "longitude", "event_date"])

# Define event type icons & colors
event_styles = {
    "Strategic developments": {"icon": "glyphicon-flag", "color": "darkblue"},
    "Battles": {"icon": "glyphicon-flash", "color": "darkred"},
    "Violence against civilians": {"icon": "glyphicon-warning-sign", "color": "black"},
    "Riots": {"icon": "glyphicon-fire", "color": "orange"},
    "Explosions/Remote violence": {"icon": "glyphicon-certificate", "color": "red"},
    "Protests": {"icon": "glyphicon-bullhorn", "color": "green"},
}

# Streamlit UI
st.title("🇺🇬 Uganda Election Event Tracker")
st.write("Click on the map to add an event location.")

# Create Folium map with a cleaner basemap
uganda_map = folium.Map(
    location=[0.3476, 32.5825],
    tiles="openstreetmap",
    zoom_start=12,
)

# Add fullscreen control (upper right corner)
Fullscreen(
    position="topleft",
    title="Expand me",
    title_cancel="Exit me",
    force_separate_button=True,
).add_to(uganda_map)

# Add existing events to the map with custom icons
for _, row in Election_df.iterrows():
    event_type = row["event_type"]
    style = event_styles.get(event_type, {"icon": "glyphicon-question-sign", "color": "gray"})

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"{event_type} ({row['event_date']})",
        tooltip=event_type,
        icon=folium.Icon(color=style["color"], icon=style["icon"]),
    ).add_to(uganda_map)

# Add a circle for the U.S. Embassy
folium.Circle(
    location=[0.29974, 32.59365],  # U.S. Embassy Kampala coordinates
    radius=500,  # Size in meters
    color="blue",
    fill=True,
    fill_color="blue",
    fill_opacity=0.3,
    popup="U.S. Embassy Kampala"
).add_to(uganda_map)

# Add existing events to the map with detailed popups
for _, row in Election_df.iterrows():
    event_type = row["event_type"]
    event_notes = row["notes"] if pd.notna(row["notes"]) else "No additional details."
    style = event_styles.get(event_type, {"icon": "glyphicon-question-sign", "color": "gray"})

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=f"<b>Type:</b> {event_type}<br><b>Date:</b> {row['event_date']}<br><b>Notes:</b> {event_notes}",
        tooltip=event_type,
        icon=folium.Icon(color=style["color"], icon=style["icon"]),
    ).add_to(uganda_map)

# Display map with Fullscreen capability
map_data = st_folium(uganda_map, width=1100, height=700)

# Extract click location
latitude = map_data["last_clicked"]["lat"] if map_data["last_clicked"] else None
longitude = map_data["last_clicked"]["lng"] if map_data["last_clicked"] else None

# Event Form (Appears After Clicking on Map)
if latitude and longitude:
    st.success(f"📍 Location Selected: {latitude}, {longitude}")
    
    event_type = st.selectbox("Select Event Type", list(event_styles.keys()))
    event_date = st.date_input("Event Date")
    event_notes = st.text_area("Additional Notes (Optional)", placeholder="Enter details about the event...")

    if st.button("Submit Event"):
        new_data = pd.DataFrame([[event_type, latitude, longitude, event_date, event_notes]], 
                                columns=["event_type", "latitude", "longitude", "event_date", "notes"])
        new_data.to_csv("Uganda_Election_Events.csv", mode="a", header=False, index=False)
        st.success("Event added! Refresh to see updates.")