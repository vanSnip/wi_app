import streamlit as st
from functools import partial

# --- CSS styling ---
st.markdown(
    """
    <style>
      .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        padding: 0.5em 1.2em;
        font-size: 1em;
        margin: 0.5em 0;
        width: 100% !important;
        display: block;
        box-sizing: border-box;
      }
      .stButton > button:hover {
        background-color: #0056b3;
      }
      .back-button > button {
        background-color: #6c757d !important;
        margin-top: 1em;
        width: 100% !important;
        display: block;
        box-sizing: border-box;
      }
      .back-button > button:hover {
        background-color: #5a6268 !important;
      }
      body {
        font-family: Arial, sans-serif;
        background-color: #f9f9f9;
        color: #333;
        padding: 2em;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Initialize session state ---
if "history" not in st.session_state:
    st.session_state.history = [("welcome", None)]

if "notificationsEnabled" not in st.session_state:
    st.session_state.notificationsEnabled = {"weather": False, "crop": False}

if "version" not in st.session_state:
    st.session_state.version = "data_saving"

if "version_show" not in st.session_state:
    st.session_state.version_show = "Data Saving Version"

cropPrices = {
    "crop_1": 215.25,
    "crop_2": 187.5,
}

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

# --- Screens ---
def render_welcome(_=None):
    st.header("Welcome, what would you like to know?")
    st.button("Weather information", on_click=partial(navigate, "weather_info"))
    st.button("Crop Advice", on_click=partial(navigate, "crop_advice_1"))
    st.button("Price information for crops", on_click=partial(navigate, "price_info_1"))
    st.button("Good Agricultural Practices", on_click=partial(navigate, "GAP_1"))
    st.button("Notifications", on_click=partial(navigate, "notifications_1"))
    st.button("Version", on_click=partial(navigate, "version_1"))
    # No back button on welcome screen

def back_button():
    if st.button("Back to previous step", key="back_button", on_click=go_back):
        pass

# --- Version Screens ---
def version_1(_=None):
    st.header(f"Select the version you want (current: {st.session_state.version_show})")

    def set_version(ver, ver_show):
        st.session_state.version = ver
        st.session_state.version_show = ver_show
        go_back()  # go back to welcome screen after setting

    st.button("Data Saving", on_click=partial(set_version, "data_saving", "Data Saving Version"))
    st.button("Performance Optimised", on_click=partial(set_version, "performance", "Performance Optimised Version"))
    st.button("Extension Officers Version", on_click=partial(set_version, "extension", "Extension Officers Version"))
    back_button()

# --- Weather Info Screens ---
def weather_info(_=None):
    st.header("Weather Information")
    version = st.session_state.version
    if version == "performance":
        st.image("https://raw.githubusercontent.com/vanSnip/wi_app/main/graphs/Nahss%20log.png", use_column_width=True)
    elif version == "extension":
        st.image("https://raw.githubusercontent.com/vanSnip/wi_app/main/graphs/Nahss%20log.png", use_column_width=True)
    else:
        st.write("Weather graphics are not available in this version to save data.")

    st.button("Go to forecasts", on_click=partial(navigate, "weather_forecasts_1"))
    st.button("Get weather advice for crops", on_click=partial(navigate, "weather_crop_advice_1"))
    back_button()

def weather_forecasts_1(_=None):
    st.header("Weather Forecasts")
    st.button("Get forecast for period 1", on_click=partial(navigate, "weather_forecasts_2", "period_1"))
    st.button("Get forecast for period 2", on_click=partial(navigate, "weather_forecasts_2", "period_2"))
    back_button()

def weather_forecasts_2(period):
    st.header(f"Forecast for {period}")
    # Replace {Insert uploaded graph} with actual graphs if available
    st.write("Test content")
    st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png", width=300)
    back_button()

def weather_crop_advice_1(_=None):
    st.header("For what crop do you need weather advice?")
    st.button("Crop 1", on_click=partial(navigate, "weather_crop_advice_3", "crop_1"))
    st.button("Crop 2", on_click=partial(navigate, "weather_crop_advice_3", "crop_2"))
    back_button()

def weather_crop_advice_3(crop):
    st.header(f"Weather advice for {crop}")
    st.write("Insert crop-specific weather advice here...")
    back_button()

# --- Crop Advice Screens ---
def crop_advice_1(_=None):
    st.header("For what crop do you need advice?")
    st.button("Cultivation", on_click=partial(navigate, "crop_advice_2", "cultivation"))
    st.button("Pest and diseases", on_click=partial(navigate, "crop_advice_2", "pest_and_diseases"))
    back_button()

def crop_advice_2(type_):
    if type_ == "pest_and_diseases":
        st.header("What type of crop do you need advice for pest and disease management?")
        st.button("Crop 1", on_click=partial(navigate, "pnd_1", "crop_1"))
        st.button("Crop 2", on_click=partial(navigate, "pnd_1", "crop_2"))
    else:
        st.header("For what crop do you need advice?")
        st.button("Crop 1", on_click=partial(navigate, "crop_cultivation_adv", "crop_1"))
        st.button("Crop 2", on_click=partial(navigate, "crop_cultivation_adv", "crop_2"))
    back_button()

def pnd_1(crop):
    st.header(f"Pest and Disease advice for {crop}")
    st.write("Insert pest and disease advice here...")
    back_button()

def crop_cultivation_adv(crop):
    st.header(f"Cultivation advice for {crop}")
    st.write("Insert cultivation advice here...")
    back_button()

# --- Price Info Screens ---
def price_info_1(_=None):
    st.header("What crop do you want to know the historical prices of?")
    st.button(f"Crop 1 - ${cropPrices['crop_1']:.2f}", on_click=partial(navigate, "price_info_2", "crop_1"))
    st.button(f"Crop 2 - ${cropPrices['crop_2']:.2f}", on_click=partial(navigate, "price_info_2", "crop_2"))
    back_button()

def price_info_2(crop):
    st.header(f"Historical price data for {crop}")
    st.write("Insert table and location info here...")
    back_button()

# --- Good Agricultural Practices Screens ---
def GAP_1(_=None):
    st.header("What type of Good Agricultural Practices do you want to know about?")
    st.button("Conservation Agriculture", on_click=partial(navigate, "GAP_2", "Conservation_agriculture"))
    st.button("3 principles of conservation agriculture", on_click=partial(navigate, "GAP_2", "three_principles"))
    st.button("Step by Step guide", on_click=partial(navigate, "GAP_2", "SBS_guide"))
    back_button()

def GAP_2(type_):
    if type_ == "Conservation_agriculture":
        st.header("Conservation Agriculture")
        st.write("Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.")
    elif type_ == "three_principles":
        st.header("Three principles of conservation agriculture")
        st.write("""
        - Minimal soil disturbance  
        - Permanent soil cover  
        - Diversity in crop rotations  
        """)
    elif type_ == "SBS_guide":
        st.header("Step by Step guide to implementing Good Agricultural Practices")
        st.write("""
        1. Assess your current practices  
        2. Plan improvements  
        3. Implement changes gradually  
        4. Monitor and adjust as needed  
        """)
    back_button()

# --- Notifications Screens ---
def notifications_1(_=None):
    st.header("What type of notifications would you like to receive?")

    weather_label = "Deactivate Weather Alerts" if st.session_state.notificationsEnabled["weather"] else "Activate Weather Alerts"
    st.button(weather_label, on_click=toggle_weather_alerts)
    st.button("Crop Cultivation", on_click=partial(navigate, "notifications_2", "crop_cultivation"))
    st.button("Price Updates", on_click=partial(navigate, "notifications_2", "price_updates"))
    if st.button("To begin"):
        reset()
    back_button()

def toggle_weather_alerts():
    st.session_state.notificationsEnabled["weather"] = not st.session_state.notificationsEnabled["weather"]

def notifications_2(type_):
    if type_ == "crop_cultivation":
        st.header("Toggle notifications for crops")
        st.button("For crop 1", on_click=partial(toggle_crop_alerts, "crop_1"))
        st.button("For crop 2", on_click=partial(toggle_crop_alerts, "crop_2"))
    elif type_ == "price_updates":
        st.header("What crop price updates would you like to receive?")
        st.button("About crop 1", on_click=partial(toggle_price_alerts, "crop_1"))
        st.button("About crop 2", on_click=partial(toggle_price_alerts, "crop_2"))
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
    "weather_forecasts_1": weather_forecasts_1,
    "weather_forecasts_2": weather_forecasts_2,
    "weather_crop_advice_1": weather_crop_advice_1,
    "weather_crop_advice_3": weather_crop_advice_3,
    "crop_advice_1": crop_advice_1,
    "crop_advice_2": crop_advice_2,
    "pnd_1": pnd_1,
    "crop_cultivation_adv": crop_cultivation_adv,
    "price_info_1": price_info_1,
    "price_info_2": price_info_2,
    "GAP_1": GAP_1,
    "GAP_2": GAP_2,
    "notifications_1": notifications_1,
    "notifications_2": notifications_2,
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
