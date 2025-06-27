# weather_utils.py
import os
import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta



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
GITHUB_TOKEN = "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"  # paste token exactly
GITHUB_REPO = "yourusername/wi_app" 
GITHUB_BRANCH = "main"
GITHUB_GRAPH_DIR = "graphs"  # Directory in your repo

def get_lon_lat_data(place_name, df=coord_data):
    """
    Returns latitude, longitude, population, and geonameid for a given place name (case-insensitive).
    If multiple matches exist, returns the top one with highest population.
    """
    place_name = place_name.lower()

    # Filter rows where name matches place_name (case-insensitive)
    matches = df[df["name"].str.lower() == place_name]

    if matches.empty:
        return None  # or raise Exception("Place not found")

    # Sort by population descending and pick top one
    best_match = matches.sort_values("population", ascending=False).iloc[0]

    return (
        float(best_match["latitude"]),
        float(best_match["longitude"]),
        int(best_match["population"]),
        best_match["geonameid"]
    )

def get_nasa_power_weather(lat, lon, months=6):

    end_date = datetime.today()
    start_date = end_date - relativedelta(months=months)

    start_dt = start_date.strftime("%Y%m%d")
    end_dt = end_date.strftime("%Y%m%d")

    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point?"
        f"start={start_dt}&end={end_dt}&latitude={lat}&longitude={lon}"
        f"&community=SB&parameters=T2M,PRECTOT&format=JSON"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")

    data = response.json()

    try:
        param_data = data['properties']['parameter']
        temp_data = param_data.get("T2M", {})
        precip_data = param_data.get("PRECTOT", {})

        if not temp_data:
            raise Exception("Temperature (T2M) data missing")
        
        dates = list(temp_data.keys())
        df = pd.DataFrame({
            "date": pd.to_datetime(dates),
            "Temperature_C": list(temp_data.values()),
            "Precipitation_mm": [precip_data.get(d, None) for d in dates],
        })

        df.set_index("date", inplace=True)
        return df

    except Exception as e:
        print("Raw API data:", data)
        raise Exception(f"Data parsing failed: {e}")

def create_weather_plot(city="Hanoi", coor_data=coord_data, label="Location", months=6):

    lat, lon, _, _ = get_lon_lat_data(city, coord_data)
    df = get_nasa_power_weather(lat, lon, months)
    period_text = f"{months}_months"
    
    filename = f"{city.replace(' ', '_').lower()}_{period_text.replace(' ', '_')}.png"
    path = os.path.join("graphs", filename)
    
    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df["Temperature_C"], color='tab:red', linewidth=2)
    plt.title(f"Daily Temperature in {label} (last {period_text})", fontsize=14)
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    plt.close()
    return filename

def upload_to_github(local_file_path, github_filename):
    with open(local_file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_GRAPH_DIR}/{github_filename}"
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
