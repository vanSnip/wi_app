#import os

import streamlit as st
from functools import partial
import pandas as pd
import requests
import ast

user = "vanSnip"  # GitHub username
repo = "wi_app"  # GitHub repository name
repo_url = f"https://raw.githubusercontent.com/{user}/{repo}/main"

#-- import data --
def load_list_from_github(filename):
    url = f"{repo_url}/scalability/{filename}"
    response = requests.get(url)
    if response.status_code == 200:
        return ast.literal_eval(response.text)  # Safe parsing of list string
    else:
        return 

def load_crop_prices():
    url = f"{repo_url}/price_data/crop_prices.csv"
    df = pd.read_csv(url, sep=',')

    # Clean column names
    df.columns = df.columns.str.strip()

    # Drop rows with missing values
    df.dropna(subset=["crop", "price"], inplace=True)

    # Strip whitespace from crop names
    df["crop"] = df["crop"].str.strip()

    return dict(zip(df["crop"], df["price"]))
    
def load_todays_climate_data():
    url = f"{repo_url}/climate_data/weather_data_today.csv"

    df = pd.read_csv(url, sep=',')
    
    # Clean column names
    df.columns = df.columns.str.strip()

    # Strip whitespace in key column
    df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.strip()

    # Convert to dictionary: key = first column, value = list of the rest
    data_dict = df.set_index(df.columns[0]).apply(lambda row: row.tolist(), axis=1).to_dict()

    return data_dict
    
crops = load_list_from_github("selected_crops.txt")   
cities = load_list_from_github("selected_cities.txt")
periods = load_list_from_github("selected_periods.txt")    

todays_climate_data = load_todays_climate_data()
cropPrices = load_crop_prices()

#-- import text --
def load_texts(filename):
    url = f"{repo_url}/texts/{filename}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return "Text not available."
#We fetch text in dict form {crop_info_class; text} (Later stage, now separate .txt files)

# --- CSS styling ---
st.markdown(
    """
    <style>
      /* Default buttons */
      div[data-testid="stButton"] > button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1.2em;
        font-size: 1em;
        margin: 0.5em 0;
        width: 100% !important;
        display: block;
        box-sizing: border-box;
        transition: background-color 0.3s ease;
      }
      div[data-testid="stButton"] > button:hover {
        background-color: #0056b3;
      }

      /* Back button */
      div[data-testid="stButton"][id="back_button"] > button {
        background-color: #ff8800 !important;
        color: white !important;
        border-radius: 5px !important;
        width: 100% !important;
        margin-top: 1em !important;
        box-sizing: border-box;
      }
      div[data-testid="stButton"][id="back_button"] > button:hover {
        background-color: #cc6f00 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

#--Get forecast graphs--
def get_forecast(period):
    # Map each period to its image filename
    filename = f"forecast_graph_for_{period}.png"
    # Full URL from your GitHub repo (use raw.githubusercontent.com)
    url = f"{repo_url}/graphs/{filename}"
    return url

# --- Initialize session states ---
if "history" not in st.session_state:
    st.session_state.history = [("welcome", None)]

if "notificationsEnabled" not in st.session_state:
    st.session_state.notificationsEnabled = {
        "weather": False,
        **{f"crop_{crop.lower().replace(' ', '_')}": False for crop in crops},
        **{f"price_{crop.lower().replace(' ', '_')}": False for crop in crops},
    }

if "version" not in st.session_state:
    st.session_state.version = "data_saving"

if "version_show" not in st.session_state:
    st.session_state.version_show = "Data Saving Version"
    
if "loc" not in st.session_state:
    st.session_state.loc = "Ho Chi Minh City"

if "selected_period" not in st.session_state:
    st.session_state.selected_period = 1
    
if "plot_url" not in st.session_state:
    st.session_state.plot_url = None

#-- define functions --
def toggle_notification(key):
    st.session_state.notificationsEnabled[key] = not st.session_state.notificationsEnabled[key]


# --- Navigation helpers ---
def navigate(screen_name, param=None):
    st.session_state.history.append((screen_name, param))

def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()

def reset():
    st.session_state.history = [("welcome", None)]
    st.session_state.notificationsEnabled = {"weather": False, "crop": False}
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"
    st.session_state.loc = "Ho Chi Minh City"

# --- Screens ---
def render_welcome(_=None):
    st.header("Xin Chao, what would you like to know? ")
    version = st.session_state.version
    if version == "data_saving":
        st.info("The current versions is the data saving version, if you want acces to pictures, please change the setting with the button \"Version and Locations\" " )
    st.button("Weather information", on_click=partial(navigate, "weather_info"))
    st.button("Crop Advice", on_click=partial(navigate, "crop_advice_1"))
    st.button("Crop Prices", on_click=partial(navigate, "price_info_1"))
    st.button("Alternative Techniques", on_click=partial(navigate, "GAP_1"))
    st.button("Notifications", on_click=partial(navigate, "notifications_1"))
    st.button("Version and Locations", on_click=partial(navigate, "version_1"))
    # No back button on welcome screen

def back_button():
    st.button("Back to previous step", key="back_button", on_click=go_back)
        

# --- Version Screens ---
def version_1(_=None):
    st.header(f"Select the version you want (current version: {st.session_state.version_show})")

    def set_version(ver, ver_show):
        st.session_state.version = ver
        st.session_state.version_show = ver_show
        go_back()  # go back to welcome screen after setting

    st.button("Data Saving Version", on_click=partial(set_version, "data_saving", "Data Saving Version"))
    st.button("Performance Optimised Version", on_click=partial(set_version, "performance", "Performance Optimised Version"))
    st.button("Extension Officers Version", on_click=partial(set_version, "extension", "Extension Officers Version"))
    st.button("Choose Location", on_click=partial(navigate, "set_location"))
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))
    
#-- Set Location --
def set_location(_=None):
    st.header(f"Select your location (your current location is: {st.session_state.loc})")

    def set_location_state(loc):
        st.session_state.loc = loc
        go_back()

    for city in cities:
        st.button(city, on_click=partial(set_location_state, city))
    back_button()

def weather_forecast_period(_=None):
    st.header(f"Select forecast period for {st.session_state.loc}")

    def select_period(months):
        st.session_state.selected_period = months
        city = st.session_state.loc
        filename = f"forecast_graph_{city.replace(' ', '_').lower()}_{months}_months.png"
        github_url = f"{repo_url}/graphs/{filename}"

        if requests.get(github_url).status_code == 200:
            st.session_state.plot_url = github_url
        navigate("weather_forecast_graph")

    for p in periods:
        st.button(f"{p} week{'s' if p > 1 else ''}", on_click=partial(select_period, p)) #now weeks
    back_button()

def weather_forecast_graph(_=None):
    city = st.session_state.loc
    months = st.session_state.selected_period
    plot_url = st.session_state.plot_url
    st.header(f"Weather in {city} - Last {months} week{'s' if months > 1 else ''}")#now weeks
    st.image(plot_url, caption=f"Temperature in {city}", use_column_width=True)
    back_button()

# --- Weather Info Screens ---
def weather_info(_=None):
    st.header("Weather Information")

    loc = st.session_state.loc
    if loc in todays_climate_data:
        temp, precip = todays_climate_data[loc]
        st.write(f"**Location:** {loc}")
        st.write(f"**Temperature:** {temp} °C")
        st.write(f"**Precipitation:** {precip} mm")
    else:
        st.warning(f"No weather data found for **{loc}**.")
    version = st.session_state.version

    
    if version == "performance":
        st.image(f"{repo_url}/graphs/Nahss%20log.png", use_column_width=True)
        st.button("Go to forecasts", on_click=partial(navigate, "weather_forecast_period"))
    elif version == "extension":
        st.image(f"{repo_url}/graphs/Nahss%20log.png", use_column_width=True)
        st.button("Go to forecasts", on_click=partial(navigate, "weather_forecast_period"))
    else:
        st.info("Weather graphics are not available in this version to save data. Change version for the forecasts")
        
    
    st.button("Get weather advice for crops", on_click=partial(navigate, "weather_crop_advice_1"))
    back_button()

def weather_forecasts_2(period):
    st.header(f"Forecast for {period}")
    graph_url = get_forecast(period)
    st.image(graph_url, caption=f"Forecast for {period}", use_column_width=True)
    back_button()

def weather_crop_advice_1(_=None):
    st.header("For what crop do you need weather advice?")
    for crop in crops:
        crop_key = crop.lower().replace(" ", "_")
        st.button(crop, on_click=partial(navigate, "weather_crop_advice_3", crop_key))
    back_button()

def weather_crop_advice_3(crop):
    st.header(f"Weather advice for {crop}")
    st.write("Insert crop-specific weather advice here...")
    back_button()

# --- Crop Advice Screens ---
def crop_advice_1(_=None):
    st.header("What type of advice do you need?")
    st.write("""**General Useful Tips:** \n
        - Try machines if possible — they save time and labor. 
        - Try to follow the planting calendar for your area. 
        - Too much water or no water can hurt the crop. 
        - Too much fertiliser causes weak plants. Use fertiliser in parts.
        - Ask your local farming officer for help. 
    """)
    st.button("Cultivation", on_click=partial(navigate, "crop_advice_2", "cultivation"))
    st.button("Pest and diseases", on_click=partial(navigate, "crop_advice_2", "pest_and_diseases"))
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))

def crop_advice_2(type_):
    if type_ == "pest_and_diseases":
        st.header("What type of crop do you need advice for pest and disease management?")
        for crop in crops:
            crop_key = crop.lower().replace(" ", "_")
            st.button(crop, on_click=partial(navigate, "pnd_1", crop_key))
    else:
        st.header("For what crop do you need cultivation advice?")
        for crop in crops:
            crop_key = crop.lower().replace(" ", "_")
            st.button(crop, on_click=partial(navigate, "crop_cultivation_adv", crop_key))
    back_button()

def pnd_1(crop):
    st.header(f"Pest and Disease advice for {crop}")
    temp_name = f"advice_pnd_{crop}.txt"
    text = load_texts(temp_name)
    st.text(text)
    back_button()
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))

def crop_cultivation_adv(crop):
    st.header(f"Cultivation advice for {crop}")
    temp_name = f"advice_cul_{crop}.txt"
    text = load_texts(temp_name)
    st.text(text)
    back_button()
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))

# --- Price Info Screens ---
def price_info_1(_=None):
    st.header("Welcome to the price menu, these are the most recent prices for the crops. ")

    for crop in crops:
        price = cropPrices.get(crop)
        label = f"{crop} - {price:.2f} usd per kg" if price is not None else f"{crop} - (no price available)" # this can be converted to vnd
        st.write(label)
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))

# --- Good Agricultural Practices Screens ---
def GAP_1(_=None):
    st.header("What alternative technique would you like to have explained")
    st.button("Conservation Agriculture", on_click=partial(navigate, "GAP_2", "Conservation_agriculture"))
    st.button("Aquatic Rice Farming", on_click=partial(navigate, "alt_tech", "aquatic"))
    st.button("Back to the main menu", on_click=partial(navigate, "welcome"))

def GAP_2(type_):
    if type_ == "Conservation_agriculture":
        st.header("Conservation Agriculture")
        text = load_texts("advice_guide_ca.txt")
        st.text(text)
        st.button("3 principles of conservation agriculture", on_click=partial(navigate, "GAP_2", "three_principles"))
        st.button("Step by Step guide", on_click=partial(navigate, "GAP_2", "SBS_guide"))
        back_button()
    elif type_ == "three_principles":
        st.header("Three principles of conservation agriculture")
        text= load_texts("advice_guide_3pgap.txt")
        st.text(text)
        st.button("Step by Step guide", on_click=partial(navigate, "GAP_2", "SBS_guide"))
        st.button("Back to the alternative farming methods", on_click=partial(navigate, "GAP_1"))
    elif type_ == "SBS_guide":
        st.header("Step by Step guide to implementing Good Agricultural Practices")
        text = load_texts("advice_guide_sbs.txt")
        st.text(text)
        st.button("Three principles of conservation agriculture", on_click=partial(navigate, "GAP_2", "three_principles"))
        st.button("Back to the alternative farming methods", on_click=partial(navigate, "GAP_1"))
    
def alt_tech(type_):
    if type_ == "aquatic":
        st.header("Aquatic Rice Farming")
        text = load_texts("advice_guide_riceaquaculture.txt")
        st.text(text)
    back_button()

# --- Notifications Screens ---
def notifications_1(_=None):
    st.header("What type of notifications would you like to receive? Click to switch them on or off.")

    weather_state = st.session_state.notificationsEnabled["weather"]
    weather_label = f"Weather Alerts ({'Enabled ' if weather_state else 'Disabled '})"
    st.button(weather_label, key="notif_weather", on_click=partial(toggle_notification, "weather"))

    st.button("Crop Cultivation", on_click=partial(navigate, "notifications_2", "crop_cultivation")) #time dependent push notifications
    st.button("Price Updates", on_click=partial(navigate, "notifications_2", "price_updates")) #weekly push notifications

    back_button()

def toggle_weather_alerts():
    st.session_state.notificationsEnabled["weather"] = not st.session_state.notificationsEnabled["weather"]

def notifications_2(type_):
    if type_ == "crop_cultivation":
        st.header("Toggle notifications for crops")
        for crop in crops:
            crop_name = crop.lower().replace(" ", "_")
            crop_key = f"crop_{crop_name}"
            state = st.session_state.notificationsEnabled.get(crop_key, False)
            label = f"{crop.replace('_', ' ').title()} cultivation updates ({'Enabled' if state else 'Disabled'} )"
            st.button(label, key=f"notif_{crop}", on_click=partial(toggle_notification, crop_key))
    elif type_ == "price_updates":
        st.header("What crop price updates would you like to receive?")
        for crop in crops:
            crop_key = crop.lower().replace(" ", "_")
            price_key = f"price_{crop_key}"
            state = st.session_state.notificationsEnabled.get(price_key, False)
            label = f"{crop} Price Updates ({'Enabled' if state else 'Disabled'})"
            st.button(label, key=f"notif_{price_key}", on_click=partial(toggle_notification, price_key))
    back_button()

def toggle_crop_alerts(crop):
    # Example toggle logic
    st.session_state.notificationsEnabled["crop"] = not st.session_state.notificationsEnabled["crop"]

def toggle_price_alerts(crop):
    # Placeholder toggle logic
    pass

# --- Screen dispatch map ---
screen_funcs = {
    "welcome": render_welcome,
    "version_1": version_1,
    "weather_info": weather_info,
    #"weather_forecasts_1": weather_forecasts_1,
    "weather_forecasts_2": weather_forecasts_2,
    "weather_crop_advice_1": weather_crop_advice_1,
    "weather_crop_advice_3": weather_crop_advice_3,
    "crop_advice_1": crop_advice_1,
    "crop_advice_2": crop_advice_2,
    "pnd_1": pnd_1,
    "crop_cultivation_adv": crop_cultivation_adv,
    "price_info_1": price_info_1,
    "GAP_1": GAP_1,
    "GAP_2": GAP_2,
    "alt_tech": alt_tech,
    "notifications_1": notifications_1,
    "notifications_2": notifications_2,
    "set_location": set_location,  
    "weather_forecast_period": weather_forecast_period,  
    "weather_forecast_graph": weather_forecast_graph,
}

# --- Main app ---
def main():
    screen_name, param = st.session_state.history[-1]
    if screen_name in screen_funcs:
        if param is not None:
            screen_funcs[screen_name](param)
        else:
            screen_funcs[screen_name]()
    else:
        st.error(f"Unknown screen: {screen_name}")

if __name__ == "__main__":
    main()
