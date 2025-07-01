from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  # Make sure to import this
import requests
import concurrent.futures
from dateutil.relativedelta import relativedelta
import pandas as pd
import matplotlib.pyplot as plt
import os
import base64
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import time

'''
Function 
inputs:
lat, lon: Latitude and Longitude of the location
start, end: Start and end dates in "YYYY-MM-DD" format

Outputs:
DataFrame containing daily temperature and precipitation data from NASA POWER API.

'''

# Load variables from .env file
load_dotenv()

# Access the environment variables
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
api_key = os.getenv("API_KEY")

# Column names from GeoNames documentation
columns = [
    "geonameid", "name", "asciiname", "alternatenames",
    "latitude", "longitude", "feature_class", "feature_code",
    "country_code", "cc2", "admin1_code", "admin2_code",
    "admin3_code", "admin4_code", "population", "elevation",
    "dem", "timezone", "modification_date"
]

# Load file
coord_data = pd.read_csv("text_data/VN.txt", sep="\t", names=columns, dtype=str)

# Convert lat/lon and population to numeric
coord_data["latitude"] = pd.to_numeric(coord_data["latitude"])
coord_data["longitude"] = pd.to_numeric(coord_data["longitude"])
coord_data["population"] = pd.to_numeric(coord_data["population"])

def get_nasa_power_weather(lat, lon, months=6):

    end_date = datetime.today()
    start_date = end_date - relativedelta(weeks=months)

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
    
'''
Function: get_nasa_power_weather

Inputs:
- lat (float): Latitude of the location (e.g., 10.03 for Can Tho)
- lon (float): Longitude of the location (e.g., 105.78 for Can Tho)
- start (str): Start date in "YYYY-MM-DD" format
- end (str): End date in "YYYY-MM-DD" format

Output:
- DataFrame: Contains daily temperature (°C) and precipitation (mm) data 
  for the specified location and time range, retrieved from the NASA POWER API.
'''



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

def get_weather(city, api_key=api_key):
    lon, lat, _, _ = get_lon_lat_data(city)
    if lon is None or lat is None:
        lon, lat = 106.660172, 10.762622  # Default to Ho Chi Minh City if not found
    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temp = data['main']['temp']  # Temperature in Celsius
        # Precipitation can be in 'rain' or 'snow' field, depends on weather
        precipitation = 0
        if 'rain' in data and '1h' in data['rain']:
            precipitation = data['rain']['1h']  # mm of rain in last 1 hour
        elif 'snow' in data and '1h' in data['snow']:
            precipitation = data['snow']['1h']  # mm of snow in last 1 hour

        return temp, precipitation
    else:
        print(f"Error fetching data: {data.get('message', 'Unknown error')}")
        return None, None

def get_weather_history_by_coords(city, api_key=api_key):
    lat, lon, _, _ = get_lon_lat_data(city)
    if lat is None or lon is None:
        lat, lon = 10.762622, 106.660172  # Default to Ho Chi Minh City if not found

    # Convert current time and start of the day to UNIX timestamps
    end_time = int(time.time())  # now
    start_time = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp())

    url = (
        f"http://history.openweathermap.org/data/2.5/history/city?"
        f"lat={lat}&lon={lon}&type=hour&start={start_time}&end={end_time}&appid={api_key}&units=metric"
    )

    #print("Requesting:", url)
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and 'list' in data:
        temps = []
        precips = []
        for hour_data in data['list']:
            temps.append(hour_data['main']['temp'])

            precip = 0
            if 'rain' in hour_data and '1h' in hour_data['rain']:
                precip += hour_data['rain']['1h']
            if 'snow' in hour_data and '1h' in hour_data['snow']:
                precip += hour_data['snow']['1h']
            precips.append(precip)

        avg_temp = sum(temps) / len(temps) if temps else None
        total_precip = sum(precips) if precips else 0

        return avg_temp, total_precip
    else:
        print("Error:", data.get("message", "Unknown error"))
        return None, None

def upload_to_github(filepath, repo_path):
    import base64
    import requests

    with open(filepath, "rb") as f:
        content = f.read()

    b64_content = base64.b64encode(content).decode()

    # Correctly use your variables here
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Check if file exists
    response = requests.get(url, headers=headers)

    data = {
        "message": f"Upload plot {repo_path}",
        "content": b64_content,
        "branch": GITHUB_BRANCH,
    }

    if response.status_code == 200:
        data["sha"] = response.json().get("sha")
    elif response.status_code != 404:
        print(f"GitHub API error: {response.status_code} {response.text}")
        return None

    # Upload file
    put_response = requests.put(url, headers=headers, json=data)

    if put_response.status_code in [200, 201]:
        print(f"Successfully uploaded {repo_path}")
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{repo_path}"
        return raw_url
    else:
        print(f"Failed to upload {repo_path}: {put_response.status_code} {put_response.text}")
        return None

def fetch_and_upload(city, months):
    # Get coordinates
    coords = get_lon_lat_data(city)
    if coords is None:
        print(f"Coordinates not found for {city}")
        return None
    lat, lon, _, _ = coords

    # Fetch NASA POWER weather data
    df = get_nasa_power_weather(lat, lon, months=months)
    if df.empty:
        print(f"No data for {city} for last {months} month(s)")
        return None
    df = df[df["Temperature_C"] > 0]
    # Prepare plot
    period_text = f"{months}_months"
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Temperature_C"], label="Temperature (°C)", color='tab:red')
    plt.title(f"Daily Temperature in {city} ({period_text})")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.tight_layout()

    # Filename and save path
    filename = f"forecast_graph_{city.replace(' ', '_').lower()}_{period_text.replace(' ', '_')}.png"
    current_dir = os.getcwd()
    local_path = os.path.join(current_dir, filename)
    plt.savefig(local_path, dpi=300)
    plt.close()
    # Upload to GitHub repo in graphs/ folder
    repo_path = f"graphs/{filename}"
    print(repo_path)
    url = upload_to_github(local_path, repo_path)

    # Optional: delete local file if you want to keep clean
    os.remove(local_path)

    return url



def simulate_and_upload_prices(crop, period=6, end_date=datetime.today(), initial_price=np.random.lognormal(mean=3, sigma=0.1, size=1)):
    """
    Simulate daily prices over the given date range with an AR(1)-like process:
    price_t = price_{t-1} + Normal(0,1)
    Save to CSV, upload to GitHub, then remove local file.
    
    crop: str, crop name
    start_date: datetime, simulation start
    end_date: datetime, simulation end
    initial_price: float, starting price at start_date
    upload_func: function, handles uploading file to GitHub, takes (local_path, remote_path)
    """
    start_date = end_date - relativedelta(months=period)

    # Create daily date range
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(dates)
    
    # Simulate daily price changes (normal noise)
    noise = np.random.normal(loc=0, scale=0.1, size=n_days)
    
    # Create price series as cumulative sum of noise starting from initial price
    prices = initial_price + np.cumsum(noise)
    
    # Make sure prices are positive (optional)
    prices = np.clip(prices, a_min=0.01, a_max=None)
    
    # Plot prices
    plt.figure(figsize=(10, 6))
    plt.plot(dates, prices, label=f"{crop} Price")
    plt.title(f"Simulated Daily Prices for {crop} ({period} months)")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True)

    # Save plot as PNG
    folder = "price_plots"
    os.makedirs(folder, exist_ok=True)
    plot_file = f"price_plot_{crop.lower().replace(' ', '_')}.png"
    plot_path = os.path.join(folder, plot_file)
    plt.savefig(plot_path)
    plt.close()

    # Upload plot image to GitHub
    upload_to_github(plot_path, f"price_data/{plot_file}")

    # Clean up local file
    os.remove(plot_path)
    if not os.listdir(folder):
        os.rmdir(folder)

    print(f"Plot uploaded for {crop}")

def text_upload(crop, type, text):
    """
    Uploads text data to GitHub in the specified format.
    
    crop: str, crop name
    type: str, type of text data (e.g., 'description', 'instructions')
    text: str, content to upload

    format:
    advice_{type}_{crop}.txt
    """
    folder = "text_data"
    os.makedirs(folder, exist_ok=True)
    
    filename = f"advice_{type}_{crop.lower().replace(' ', '_')}.txt"
    file_path = os.path.join(folder, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    upload_to_github(file_path, f"texts/{filename}")
    
    # Clean up local file
    os.remove(file_path)

    if not os.listdir(folder):
        os.rmdir(folder)