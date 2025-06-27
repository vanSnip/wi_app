# weather_utils.py
import os
import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
load_dotenv()
import os

token = os.getenv("GITHUB_TOKEN")

# Column names from GeoNames documentation
columns = [
    "geonameid", "name", "asciiname", "alternatenames",
    "latitude", "longitude", "feature_class", "feature_code",
    "country_code", "cc2", "admin1_code", "admin2_code",
    "admin3_code", "admin4_code", "population", "elevation",
    "dem", "timezone", "modification_date"
]

# Load file
coord_data = pd.read_csv("VN.txt", sep="\t", names=columns, dtype=str)

# Convert lat/lon and population to numeric
coord_data["latitude"] = pd.to_numeric(coord_data["latitude"])
coord_data["longitude"] = pd.to_numeric(coord_data["longitude"])
coord_data["population"] = pd.to_numeric(coord_data["population"])

# Set this to your GitHub token (use env variable for security)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # You must export this in your environment
GITHUB_REPO = "yourusername/wi_app" 
GITHUB_BRANCH = "main"
GITHUB_GRAPH_DIR = "graphs"  # Directory in your repo

def get_lon_lat_data(place_name, df):
    place_name = place_name.lower()
    matches = df[df["name"].str.lower() == place_name]
    if matches.empty:
        raise Exception(f"Place '{place_name}' not found")
    best_match = matches.sort_values("population", ascending=False).iloc[0]
    return float(best_match["latitude"]), float(best_match["longitude"])

def get_nasa_power_weather(lat, lon, months=6):
    end_date = datetime.today()
    start_date = end_date - relativedelta(months=months)
    start_dt = start_date.strftime("%Y%m%d")
    end_dt = end_date.strftime("%Y%m%d")
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"start={start_dt}&end={end_dt}&latitude={lat}&longitude={lon}"
        f"&community=SB&parameters=T2M&format=JSON"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")
    data = response.json()
    temp_data = data["properties"]["parameter"]["T2M"]
    df = pd.DataFrame({
        "date": pd.to_datetime(list(temp_data.keys())),
        "Temperature_C": list(temp_data.values())
    })
    df.set_index("date", inplace=True)
    df["Temperature_C"] = df["Temperature_C"].astype(float)
    df = df[df["Temperature_C"] > 0]
    return df

def create_weather_plot(city, months, coord_data):
    lat, lon = get_lon_lat_data(city, coord_data)
    df = get_nasa_power_weather(lat, lon, months)
    period_text = f"{months} month{'s' if months > 1 else ''}"
    filename = f"{city.replace(' ', '_').lower()}_{period_text.replace(' ', '_')}.png"

    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df["Temperature_C"], color='tab:red', linewidth=2)
    plt.title(f"Daily Temperature in {city} (last {period_text})", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    return filename

def upload_to_github(local_file_path, github_filename):
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_GRAPH_DIR}/{github_filename}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {
        "message": f"Add plot {github_filename}",
        "branch": GITHUB_BRANCH,
        "content": content,
    }

    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        raise Exception(f"GitHub upload failed: {response.status_code} - {response.text}")
    
    return response.json()["content"]["download_url"]
