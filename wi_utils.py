#import base64
#import concurrent.futures

#time manipulation
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta  
import time

#the data manipulation
import pandas as pd
import numpy as np

# Plotting tools
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# interaction with external APIs and files
import re
import os
import json
from dotenv import load_dotenv
from lxml import html
import requests

'''
Initiate the global variables
'''

# Load variables from .env file
load_dotenv(override=True)

# Access the environment variables
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
weather_api_key = os.getenv("weather_API_KEY")
fx_API_KEY = os.getenv("fx_API_KEY")

user = "vanSnip"  # GitHub username
repo = "wi_app"  # GitHub repository name
repo_url = f"https://raw.githubusercontent.com/{user}/{repo}/main"

'''
initiate the columns for the GeoNames data
'''
# Column names from GeoNames documentation, these are for the coordinates
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

viet_coord_data = pd.read_csv("text_data/VN.txt", sep="\t", names=columns, dtype=str)



'''
Start Functions 1: location and weather data
'''

'''
Function: get_nasa_power_weather
inputs:
lat, lon: Latitude and Longitude of the location
start, end: Start and end dates in "YYYY-MM-DD" format

Outputs:
DataFrame containing daily temperature and precipitation data from NASA POWER API.

'''

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
Function: get_lon_lat_data
Inputs:
place_name: String name of the place to look up (case-insensitive).
df: Optional pandas DataFrame containing location data with columns ["name", "latitude", "longitude", "population", "geonameid"] (default is coord_data).

Outputs:
Tuple containing (latitude: float, longitude: float, population: int, geonameid) of the best matching place by name.
Returns None if no matching place is found.
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

'''
Function: get_weather
Inputs:
city: String name of the city to fetch weather for.
api_key: API key string for OpenWeatherMap (default taken from variable api_key).

Outputs:
Tuple containing (temperature in Celsius: float, precipitation in mm over last hour: float).
Returns (None, None) if there is an error or city not found.
'''

def get_weather(city, api_key=weather_api_key):
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

"""
Retrieves the latest hourly temperature, precipitation, and wind speed for a specified city,
along with their corresponding averages over the past `days` period using OpenWeatherMap's
historical hourly API.

Parameters:
    city (str): The name of the city to retrieve weather data for.
    days (int): Number of past days to include for averaging (default is 3).

Returns:
    tuple:
        latest_temp (float): Most recent temperature in Celsius.
        latest_precip (float): Most recent precipitation in mm.
        latest_wind (float): Most recent wind speed in m/s.
        avg_temp (float): Average temperature over the past `days` in Celsius.
        avg_precip (float): Average precipitation over the past `days` in mm.
        avg_wind (float): Average wind speed over the past `days` in m/s.

Notes:
    - Falls back to coordinates for Ho Chi Minh City if the city cannot be resolved.
    - Returns (0, 0, 0, 0, 0, 0) if the API request fails or no data is found.
    - Precipitation includes both rainfall and snowfall when available.
"""

def get_past_days_average_by_coords(city, days=10):
    lat, lon, *_ = get_lon_lat_data(city)
    if lat is None or lon is None:
        lat, lon = 10.762622, 106.660172

    end_time = int(time.time())
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())

    url = (
        f"http://history.openweathermap.org/data/2.5/history/city?"
        f"lat={lat}&lon={lon}&type=hour&start={start_time}&end={end_time}&appid={weather_api_key}&units=metric"
    )

    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and 'list' in data:
        temps, precips, winds = [], [], []
        for hour in data['list']:
            temps.append(hour['main']['temp'])

            # Precipitation
            precip = 0
            if 'rain' in hour and '1h' in hour['rain']:
                precip += hour['rain']['1h']
            if 'snow' in hour and '1h' in hour['snow']:
                precip += hour['snow']['1h']
            precips.append(precip)

            # Wind
            winds.append(hour['wind']['speed'])

        avg_temp = sum(temps) / len(temps) if temps else 0
        avg_precip = sum(precips)/ len(precips) if precips else 0
        avg_wind = sum(winds) / len(winds) if winds else 0

        return round(temps[-1], 2), round(precips[-1], 2), round(winds[-1], 2), round(avg_temp, 2), round(avg_precip, 2), round(avg_wind, 2)

    return 0, 0, 0, 0, 0, 0

"""
Classifies a current observed value relative to a historical average, using a specified tolerance.

Parameters:
    today (float): The current observed value.
    historical_avg (float): The historical average value to compare against.
    tolerance (float): The relative deviation (as a fraction of the average) within which the value is 
                        considered "about average". Default is 0.3 (i.e., ±30%).

Returns:
    str: A qualitative classification:
        - "about average" if the value deviates within ±tolerance * historical_avg,
        - "above average" if the value is significantly greater than the average,
        - "below average" if the value is significantly less than the average,
        - "undefined" if the historical average is zero (to avoid division by zero).

Notes:
    This function is useful for interpreting weather or climate data against historical baselines.
"""

def classify_value(today, historical_avg, tolerance=0.3):
    """
    Compares today's value against historical average.
    Tolerance is fraction of historical avg (default 30%).
    """
    if historical_avg == 0:
        return "undefined"

    if abs(today - historical_avg) <= tolerance * historical_avg:
        return "about average"
    elif today > historical_avg:
        return "above average"
    else:
        return "below average"

"""
Function: gen_graphs_cities_periods
Runs fetch_and_upload for each city and period combination.

Args:
    selected_cities (list of str): List of city names to process.
    selected_periods (list of int): List of periods in months.

Returns:
    dict: Nested dictionary with structure {city: {months: uploaded_url or None}}
"""

def gen_graphs_cities_periods(selected_cities, selected_periods):

    results = {}
    for city in selected_cities:
        results[city] = {}
        for months in selected_periods:
            print(f"Processing {city} for {months} month(s)...")
            uploaded_url = fetch_and_upload(city, months)
            results[city][months] = uploaded_url
    return results

"""
Collects current weather conditions and classifies them relative to recent historical averages 
for a list of cities, then stores the results in a CSV file and uploads it to a GitHub repository.

Parameters:
    cities (list of str): List of city names for which weather data should be retrieved.
    folder (str): Name of the local directory used for storing the temporary CSV file. 
                    Defaults to "climate_data".

Returns:
    str: URL of the uploaded CSV file on GitHub if successful; otherwise, None.

Description:
    For each city, this function retrieves:
        - Today's temperature, precipitation, and wind speed using current weather data.
        - Historical average values for the past several days.
    It then classifies each metric (temperature, precipitation, wind speed) as "above average", 
    "below average", or "about average" compared to historical norms using a tolerance threshold.

    The collected and classified data is saved in a structured format as a CSV file. 
    The file is uploaded to a GitHub repository via the GitHub REST API, and the local file is deleted afterward.

Notes:
    - This function depends on `get_past_days_average_by_coords`, `classify_value`, and `upload_to_github`.
    - The output CSV contains nested dictionaries; for readability or compatibility with some tools, 
        consider flattening the structure.
"""

def collect_and_upload_weather_data(cities, folder="climate_data"):
    import os
    import pandas as pd

    os.makedirs(folder, exist_ok=True)
    weather_data = []

    for city in cities:

        temp, precip, wind, hist_temp, hist_precip, hist_wind = get_past_days_average_by_coords(city)

        # Classify current vs historical
        temp_label = classify_value(temp, hist_temp)
        precip_label = classify_value(precip, hist_precip)
        wind_label = classify_value(wind, hist_wind)

        weather_data.append({
            "city": city,
            "today_values": {
                "temperature": round(temp, 2),
                "precipitation": round(precip, 2),
                "wind_speed": round(wind, 2)
            },
            "classifications": {
                "temp_classification": temp_label,
                "precip_classification": precip_label,
                "wind_classification": wind_label
            }
        })

    df = pd.DataFrame(weather_data)
    save_file_path = os.path.join(folder, "weather_data_today.csv")
    df.to_csv(save_file_path, index=False)
    uploaded_url = upload_to_github(save_file_path, f"{folder}/weather_data_today.csv")

    os.remove(save_file_path)
    return uploaded_url

'''
Start Functions 2: GitHub upload
'''

'''
Function: upload_to_github
Inputs:
- filepath: Local path to the file you want to upload.
- repo_path: Path within the GitHub repository where the file will be uploaded.

Outputs:
- On success: Returns the raw GitHub URL of the uploaded file.
- On failure: Prints an error message and returns None.

Notes:
- Requires environment variables or global variables GITHUB_REPO, GITHUB_TOKEN, and GITHUB_BRANCH
  to be set appropriately.
- Uses GitHub REST API to create or update the file in the repo.
'''

def upload_to_github(filepath, repo_path):
    import base64
    import requests

    # Debug: Print environment variables (not the token itself)
    """
    print("GITHUB_TOKEN:", repr(GITHUB_TOKEN))
    print("GITHUB_REPO:", repr(GITHUB_REPO))
    print("GITHUB_BRANCH:", repr(GITHUB_BRANCH))
    """

    with open(filepath, "rb") as f:
        content = f.read()

    b64_content = base64.b64encode(content).decode()

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Check if file exists
    response = requests.get(url, headers=headers)

    #print(f"GET {url} status: {response.status_code}, response: {response.text}")

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
    #print(f"PUT {url} status: {put_response.status_code}, response: {put_response.text}")

    if put_response.status_code in [200, 201]:
        print(f"Successfully uploaded {repo_path}")
        raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/{repo_path}"
        return raw_url
    else:
        print(f"Failed to upload {repo_path}: {put_response.status_code} {put_response.text}")
        return None

'''
Function: fetch_and_upload
Inputs:
- city: Name of the city to fetch weather data for.
- months: Number of months of historical weather data to fetch.

Process:
- Gets city coordinates.
- Fetches NASA POWER weather data for given months.
- Filters out non-positive temperatures.
- Plots daily temperature and saves as PNG.
- Uploads the plot to GitHub under 'graphs/' folder.
- Deletes the local plot file after upload.

Outputs:
- Returns the raw GitHub URL of the uploaded plot image if successful.
- Returns None if any step fails.
'''

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

"""
Uploads text data to GitHub in the specified format.

crop: str, crop name
type: str, type of text data (e.g., 'description', 'instructions')
text: str, content to upload

format:
advice_{type}_{crop}.txt
"""

def text_upload(crop, type, text):

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


"""
Function: save_and_upload_lists

Save multiple lists to text files (as string representations) in the given folder,
then upload each file to GitHub.

Args:
    data_dict (dict): Keys are filenames (without extension), values are lists to save.
    folder (str): Folder to save files locally and in repo path.

Example:
    save_and_upload_lists({
        "selected_cities": selected_cities,
        "selected_periods": selected_periods,
        "selected_crops": selected_crops,
    })
"""

def save_and_upload_lists(data_dict, folder="scalability"):
    os.makedirs(folder, exist_ok=True)

    for name, data_list in data_dict.items():
        save_file_path = os.path.join(folder, f"{name}.txt")
        with open(save_file_path, "w") as f:
            f.write(str(data_list))

        repo_path = f"{folder}/{name}.txt"
        upload_to_github(save_file_path, repo_path)

def upload_csv(filtered_cities, folder="csv_files", filename="filtered_cities.csv"):

    os.makedirs(folder, exist_ok=True)

    save_file_path = os.path.join(folder, filename)
    filtered_cities.to_csv(save_file_path, index=False)

    uploaded_url = upload_to_github(save_file_path, f"{folder}/{filename}")

    # Clean up local file
    os.remove(save_file_path)

    return uploaded_url

'''
start Functions 3: Prices
'''


"""
Function: fetch_vietnam_rice_price

Inputs:
    None

Outputs:
    float: Latest Vietnam 5% Broken Rice Price in USD per kilogram (converted from USD per ton)
    or
    str: Error message if fetching or parsing fails
"""

def fetch_vietnam_rice_price():
    """
    Fetches the latest Vietnam 5% Broken Rice Price (USD/ton)
    from ycharts.com using XPath scraping.
    """
    url = "https://ycharts.com/indicators/vietnam_5_broken_rice_price?utm_source=chatgpt.com"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # Fetch the page
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML
        tree = html.fromstring(response.content)

        # XPath to the rice price value
        xpath = "/html/body/main/div/div[4]/div/div/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td[2]/text()"
        price = tree.xpath(xpath)

        if price:
            return float(price[0].strip()) / 1000 # Convert usd/ton to USD/kg 
        else:
            return "Price not found"
    
    except Exception as e:
        return f"Error: {str(e)}"

"""
Function: fetch_sugar_price

Inputs:
    None

Outputs:
    float: Latest sugar price converted from cents per pound to USD per kilogram
    or
    str: Error message if data extraction or parsing fails
"""

def fetch_sugar_price():
    url = "https://tradingeconomics.com/commodity/sugar"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    html_text = response.text

    # Regex to extract the TEChartsMeta JSON array inside the script tag
    pattern = r"TEChartsMeta\s*=\s*(\[\{.*?\}\]);"
    match = re.search(pattern, html_text, re.DOTALL)

    if not match:
        return "TEChartsMeta data not found"

    json_text = match.group(1)

    # Parse JSON
    try:
        data = json.loads(json_text)
        # Extract converted_value from first item
        price = data[0]["last"]
        return float(price) * 0.0220462 #initial is cents/lb to usd kg
    except Exception as e:
        return f"Error parsing JSON: {e}"
    
"""
Function: get_vnd_to_usd_rate

Inputs:
    API_KEY (str): API key for exchangerate-api.com (default from fx_API_KEY)

Outputs:
    float: Exchange rate from USD to VND
    None: If API request fails or data is missing
"""   

def get_vnd_to_usd_rate(API_KEY=fx_API_KEY ):
    
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to get data: {response.status_code}")
        return None
    
    data = response.json()
    if data.get("result") != "success":
        print(f"API returned error: {data.get('error-type', 'Unknown error')}")
        return None
    
    rates = data.get("conversion_rates", {})
    vnd_rate = rates.get("VND")
    if vnd_rate is None:
        print("VND rate not found in data")
        return None
    
    return vnd_rate

"""
Function: fetch_vietnam_maize_price

Inputs:
    None

Outputs:
    float: Average of the first two maize prices from Selina Wamucii site (VND/kg converted to USD/kg)
    None: If fetching or parsing fails
"""

def fetch_vietnam_maize_price():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)"}
    url = "https://www.selinawamucii.com/insights/prices/vietnam/maize/"
    xpath = '//*[@id="retail-prices"]/p[2]/text()'
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        tree = html.fromstring(response.content)
        text_list = tree.xpath(xpath)

        if not text_list:
            print("No text found at the specified XPath.")
            return None

        text = text_list[0].strip()

        pattern = r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?'

        matches = re.findall(pattern, text)

        # Convert to float after removing commas
        numbers = []
        for match in matches:
            number = float(match.replace(',', ''))
            numbers.append(number)
            if len(numbers) == 2:
                break

        if len(numbers) < 2:
            print("Less than two valid numbers found.")
            return None

        return float((numbers[0] + numbers[1]) / len(numbers) / get_vnd_to_usd_rate()) # usd per kg

    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


"""
Function: save_and_upload_crop_prices
Create a DataFrame from CropPrices dict and selected_crops list,
save it as a CSV in the specified folder,
upload the CSV to GitHub using upload_to_github(),
then clean up the local file and folder if empty.

Args:
    CropPrices (dict): Mapping crop names to prices (e.g. {"Rice": 1.2, "Maize": 0.9})
    selected_crops (list): List of crop names to include in the CSV (order matters)
    folder (str): Folder to save the CSV file locally and remotely in the repo

Returns:
    None
"""

def save_and_upload_crop_prices(CropPrices, selected_crops, folder="price_data"):

    prices_list = [CropPrices.get(crop, None) for crop in selected_crops]
    crop_prices = pd.DataFrame({
        "crop": selected_crops,
        "price": prices_list
    })

    os.makedirs(folder, exist_ok=True)

    save_file_path = os.path.join(folder, "crop_prices.csv")
    crop_prices.to_csv(save_file_path, index=False)

    upload_to_github(save_file_path, f"{folder}/crop_prices.csv")

    os.remove(save_file_path)
    if not os.listdir(folder):
        os.rmdir(folder)

'''
start Functions 4: Locations
'''

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (km).
    """
    R = 6371  # Earth radius in km
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    d_phi = np.radians(lat2 - lat1)
    d_lambda = np.radians(lon2 - lon1)
    
    a = np.sin(d_phi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(d_lambda/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def filter_cities_by_distance(df, lat_col='latitude', lon_col='longitude', pop_col='population', min_distance_km=100):
    """
    Filter cities to remove those within min_distance_km of each other, prioritizing higher population.
    
    Args:
        df: DataFrame with city data
        lat_col, lon_col: column names for lat/lon
        pop_col: population column name for priority sorting
        min_distance_km: minimum allowed distance between cities (in km)
    
    Returns:
        Filtered DataFrame of cities
    """
    # Sort descending by population
    df_sorted = df.sort_values(by=pop_col, ascending=False).reset_index(drop=True)
    
    selected_indices = []
    
    for idx, row in df_sorted.iterrows():
        lat, lon = row[lat_col], row[lon_col]
        
        # Check distance to already selected cities
        too_close = False
        for sel_idx in selected_indices:
            sel_row = df_sorted.loc[sel_idx]
            dist = haversine_distance(lat, lon, sel_row[lat_col], sel_row[lon_col])
            if dist < min_distance_km:
                too_close = True
                break
        
        if not too_close:
            selected_indices.append(idx)
    
    return df_sorted.loc[selected_indices].reset_index(drop=True)

viet_coord_data["latitude"] = pd.to_numeric(viet_coord_data["latitude"], errors='coerce')
viet_coord_data["longitude"] = pd.to_numeric(viet_coord_data["longitude"], errors='coerce')
viet_coord_data = viet_coord_data.dropna(subset=["latitude", "longitude"])


"""
Searches for a city by ascii name in the filtered cities dataset.
If not found, finds the closest city within coord_threshold (degrees),
and returns a message with the closest city ascii name and distance in km.

Args:
    name (str): ASCII name of the city to search.
    filtered_cities (DataFrame): DataFrame with filtered cities including 'latitude', 'longitude', 'asciiname'.
    coord_data (DataFrame): Full dataset with cities.
    coord_threshold (float): Max degrees difference in lat/lon for filtering nearby cities.

Returns:
    str: Message with closest city ascii name and distance in km, or not found message.
"""

def search_city(name, filtered_cities, coord_data=viet_coord_data, coord_threshold=0.2):
    name = name.strip().lower()

    # Step 1: Check direct match in filtered_cities
    for _, row in filtered_cities.iterrows():
        ascii_name = str(row["asciiname"]).lower()
        std_name = str(row["name"]).lower()
        alt_names = str(row.get("alternatenames", "")).lower().split(",")

        if name == ascii_name or name == std_name or name in [alt.strip() for alt in alt_names]:
            return row["name"], f"The city '{row['asciiname']}' is found in the dataset."

    # Step 2: Find a match in full coord_data
    match_row = None
    for _, row in coord_data.iterrows():
        ascii_name = str(row["asciiname"]).lower()
        std_name = str(row["name"]).lower()
        alt_names = str(row.get("alternatenames", "")).lower().split(",")

        if name == ascii_name or name == std_name or name in [alt.strip() for alt in alt_names]:
            match_row = row
            break

    if match_row is None:
        return None, f"No matches found for '{name}'."

    city_lat = match_row["latitude"]
    city_lon = match_row["longitude"]

    # Step 3: Find cities within coordinate threshold
    nearby = filtered_cities[
        (filtered_cities["latitude"].sub(city_lat).abs() <= coord_threshold) &
        (filtered_cities["longitude"].sub(city_lon).abs() <= coord_threshold)
    ]

    if nearby.empty:
        return None, f"No nearby cities within {coord_threshold} degrees found near '{name}'."

    # Step 4: Compute Euclidean distance
    nearby = nearby.copy()
    nearby["euclid_dist_deg"] = np.sqrt(
        (nearby["latitude"] - city_lat) ** 2 +
        (nearby["longitude"] - city_lon) ** 2
    )

    # Step 5: Select closest city
    closest = nearby.nsmallest(1, "euclid_dist_deg").iloc[0]
    dist_km = closest["euclid_dist_deg"] * 111  # ~111 km per degree

    return closest["name"], f"The closest city with data is '{closest['name']}', which is approximately {dist_km:.2f} km from '{name}'."


''''
Function: plot_forecast
Inputs:
- intervals: List of time intervals (e.g., ["Today", "Tomorrow", "3rd Day", ...])
- weather: List of weather conditions (e.g., ["Sunny", "Cloudy", "Rainy", ...])
- temp: List of temperatures for each interval (e.g., ["30°C", "28°C", ...])
- wind: List of wind conditions (e.g., ["5 km/h", "10 km/h", ...])
- precip: List of precipitation conditions (e.g., ["0 mm", "2 mm", ...])
- advice: List of advice for each interval (e.g., ["Wear sunscreen", "Carry an umbrella", ...])
'''
def plot_forecast(intervals, weather, temp, wind, precip, advice, name="weather_forecast_example"):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.axis('off')
    ax.add_patch(Rectangle((0, 0), 1, 1, color='#f0f8ff'))

    icons_weather = {
        "Sunny": "☀️",
        "Cloudy": "☁️",
        "Rainy": "🌧️"
        }  
    
    # Add title
    ax.text(0.5, 1.03, " Farmer's Weather Forecast ", ha='center', fontsize=20, weight='bold')

    # Row loop
    for i in range(len(intervals)):
        y = 0.85 - i * 0.18

        # Day
        ax.text(0.04, y, intervals[i], fontsize=16, weight='bold', va='center')

        # Weather Icon
        ax.text(0.15, y, icons_weather[weather[i]], fontsize=24, va='center')

        # Temp
        ax.text(0.24, y, temp[i], fontsize=14, va='center')

        # Wind
        ax.text(0.35, y, f" {wind[i]}", fontsize=13, va='center')

        # Precipitation
        ax.text(0.5, y, f" {precip[i]}", fontsize=13, va='center')

        # Advice
        ax.text(0.65, y, advice[i], fontsize=13, va='center')

    # Column headers
    ax.text(0.04, .92, "Day", fontsize=12, weight='bold')
    ax.text(0.12, .92, "Weather", fontsize=12, weight='bold')
    ax.text(0.24, .92, "Temp", fontsize=12, weight='bold')
    ax.text(0.35, .92, "Wind", fontsize=12, weight='bold')
    ax.text(0.5, .92, "Rain", fontsize=12, weight='bold')
    ax.text(0.65, .92, "Advice", fontsize=12, weight='bold')

    # Save to file
    plt.tight_layout()
    upload_name = f"{name}.png"
    plt.savefig(f"{upload_name}", bbox_inches='tight')
    upload_to_github(upload_name, f"graphs/{upload_name}")
    plt.close()
