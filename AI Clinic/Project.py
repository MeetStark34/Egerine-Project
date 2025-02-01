import os
import time
import random
import csv
import sqlite3
import pandas as pd
import folium
from datetime import datetime

# --- Step 1: Auto-Create Required Folders & Files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CSV_FILE = os.path.join(DATA_DIR, "stored_gps_data.csv")
DB_FILE = os.path.join(DATA_DIR, "gps_data.db")
MAP_FILE = os.path.join(DATA_DIR, "bike_journey_map.html")

os.makedirs(DATA_DIR, exist_ok=True)

# --- Step 2: Ensure SQLite Database Exists ---
def setup_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gps_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

# --- Step 3: Simulate Real-Time GPS Data Streaming ---
def simulate_gps_stream(num_points=10, interval=2):
    lat, lon = 48.8566, 2.3522  # Start location (Paris)
    
    with open(CSV_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Latitude", "Longitude", "Timestamp"])

        for _ in range(num_points):
            lat += random.uniform(-0.001, 0.001)
            lon += random.uniform(-0.001, 0.001)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            writer.writerow([lat, lon, timestamp])
            print(f"Streaming GPS Data: {lat}, {lon}, {timestamp}")
            
            save_gps_to_db(lat, lon, timestamp)
            time.sleep(interval)

# --- Step 4: Store Data in SQLite Database ---
def save_gps_to_db(lat, lon, timestamp):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gps_data (latitude, longitude, timestamp) VALUES (?, ?, ?)", (lat, lon, timestamp))
    conn.commit()
    conn.close()

# --- Step 5: Generate an Interactive Map ---
def visualize_gps_data():
    if not os.path.exists(CSV_FILE):
        print("No GPS data found to plot.")
        return
    
    gps_data = pd.read_csv(CSV_FILE)
    
    if gps_data.empty:
        print("GPS data is empty. Cannot generate a map.")
        return
    
    start_lat, start_lon = gps_data.iloc[0]["Latitude"], gps_data.iloc[0]["Longitude"]
    bike_map = folium.Map(location=[start_lat, start_lon], zoom_start=14)

    for _, row in gps_data.iterrows():
        folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            popup=f"Timestamp: {row['Timestamp']}"
        ).add_to(bike_map)

    folium.PolyLine(
        locations=gps_data[["Latitude", "Longitude"]].values.tolist(),
        color="blue",
        weight=5
    ).add_to(bike_map)

    bike_map.save(MAP_FILE)
    print(f"Map saved to {MAP_FILE}")

# --- Step 6: Run Everything ---
if __name__ == "__main__":
    setup_database()
    simulate_gps_stream(num_points=20, interval=2)
    visualize_gps_data()

    print("\n✅ All steps completed successfully!")
    print(f"📄 GPS Data stored in: {CSV_FILE}")
    print(f"🗄️ Database stored in: {DB_FILE}")
    print(f"🗺️ Map available at: {MAP_FILE} (Open in browser)")