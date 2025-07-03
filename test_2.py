### Refactored Main Application Code (Streamlined for Efficiency and Clarity)

import streamlit as st
import pandas as pd
import requests
import ast
import numpy as np
from functools import partial

# --- Config ---
GITHUB_USER = "vanSnip"
REPO_NAME = "wi_app"
BASE_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main"

# --- Utility Functions ---
def fetch_text_file(path):
    url = f"{BASE_URL}/{path}"
    res = requests.get(url)
    return res.text if res.ok else None

def load_csv(path):
    return pd.read_csv(f"{BASE_URL}/{path}")

def load_list(filename):
    data = fetch_text_file(f"scalability/{filename}")
    return ast.literal_eval(data) if data else []

def get_forecast_url(period):
    return f"{BASE_URL}/graphs/forecast_graph_for_{period}.png"

def load_weather_data():
    df = load_csv("climate_data_2/weather_data_today.csv")
    df.columns = df.columns.str.strip()
    df[df.columns[0]] = df[df.columns[0]].astype(str).str.strip()
    return df.set_index(df.columns[0]).apply(list, axis=1).to_dict()

def load_prices():
    try:
        df = load_csv("price_data/crop_prices.csv")
        df.columns = df.columns.str.strip()
        df.dropna(subset=["crop", "price"], inplace=True)
        df["crop"] = df["crop"].str.strip()
        return dict(zip(df["crop"], df["price"]))
    except:
        return {}

def load_text(name):
    return fetch_text_file(f"texts/{name}") or "Text not available."

def euclidean_distance(lat1, lon1, lat2, lon2):
    return np.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

def search_city(name, cities_df, full_df, threshold=0.5):
    name = name.strip().lower()
    
    def match(row):
        names = [str(row.get(k, "")).lower() for k in ["name", "asciiname"]]
        alt_names = str(row.get("alternatenames", "")).lower().split(",")
        return name in names or name in [alt.strip() for alt in alt_names]

    match_rows = cities_df[cities_df.apply(match, axis=1)]
    if not match_rows.empty:
        row = match_rows.iloc[0]
        return row["name"], f"City '{row['asciiname']}' found."

    full_matches = full_df[full_df.apply(match, axis=1)]
    if full_matches.empty:
        return None, f"No match for '{name}'."

    ref_row = full_matches.iloc[0]
    lat, lon = ref_row["latitude"], ref_row["longitude"]
    cities_df = cities_df.copy()
    cities_df["dist"] = euclidean_distance(cities_df["latitude"], cities_df["longitude"], lat, lon)
    closest = cities_df[cities_df["dist"] <= threshold].nsmallest(1, "dist")

    if closest.empty:
        return None, f"No cities within {threshold} degrees."

    city = closest.iloc[0]
    km = city["dist"] * 111
    return city["name"], f"Closest data city: '{city['asciiname']}', approx. {km:.1f} km from '{name}'."

# --- Load Data ---
crops = load_list("selected_crops.txt")
periods = load_list("selected_periods.txt")
weather_data = load_weather_data()
crop_prices = load_prices()

filtered_cities = load_csv("csv_files/filtered_cities.csv")
columns = ["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude"]
viet_coord_data = pd.read_csv("text_data/VN.txt", sep="\t", names=columns, usecols=[0,1,2,3,4,5], dtype=str)

for df in [filtered_cities, viet_coord_data]:
    df[["latitude", "longitude"]] = df[["latitude", "longitude"]].apply(pd.to_numeric, errors="coerce")
    df.dropna(subset=["latitude", "longitude"], inplace=True)

# --- Session Init ---
def init_session():
    ss = st.session_state
    ss.setdefault("history", [("welcome", None)])
    ss.setdefault("loc", "Ho Chi Minh City")
    ss.setdefault("version", "data_saving")
    ss.setdefault("version_show", "Data Saving Version")
    ss.setdefault("selected_period", 1)
    ss.setdefault("plot_url", None)
    ss.setdefault("notificationsEnabled", {"weather": False, **{f"crop_{c.lower().replace(' ', '_')}": False for c in crops}, **{f"price_{c.lower().replace(' ', '_')}": False for c in crops}})

# --- Navigation ---
def navigate(screen, param=None):
    st.session_state.history.append((screen, param))

def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()

def back_button():
    st.button("Back", key="back_button", on_click=go_back)

# --- Main Entry Point ---
def main():
    init_session()
    screen, param = st.session_state.history[-1]
    if screen in screen_funcs:
        screen_funcs[screen](param) if param else screen_funcs[screen]()
    else:
        st.error(f"Unknown screen: {screen}")

# --- Define Screens Here (e.g., welcome, weather_info, crop_advice, etc.) ---
# Add only core logic or structure here. You can modularize screens into separate files/functions.

def render_welcome():
    st.header("Xin Chao, what would you like to know?")
    if st.session_state.version == "data_saving":
        st.info("You're using the data-saving version. Switch via 'Version and Locations'.")
    for label, screen in [
        ("Weather Information", "weather_info"),
        ("Crop Advice", "crop_advice_1"),
        ("Crop Prices", "price_info_1"),
        ("Alternative Techniques", "GAP_1"),
        ("Notifications", "notifications_1"),
        ("Version and Locations", "version_1")
    ]:
        st.button(label, on_click=partial(navigate, screen))

# --- Add other screens like weather_info, crop_advice_1, etc. ---

# --- Register Screens ---
screen_funcs = {
    "welcome": render_welcome,
    # Register more screens as you define them...
}

if __name__ == "__main__":
    main()
