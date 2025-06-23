import streamlit as st

# --- Session State Initialization ---
if "page_stack" not in st.session_state:
    st.session_state.page_stack = []
if "version" not in st.session_state:
    st.session_state.version = "data_saving"

# --- Navigation Helpers ---
def go_to(page_name):
    st.session_state.page_stack.append(page_name)
    st.experimental_rerun()

def go_back():
    if len(st.session_state.page_stack) > 1:
        st.session_state.page_stack.pop()
        st.experimental_rerun()

def render_page():
    current_page = st.session_state.page_stack[-1] if st.session_state.page_stack else "welcome"
    PAGES[current_page]()

# --- Styled Button ---
def styled_button(label, page_name):
    st.markdown(f"""
        <style>
            .custom-button {{
                background-color: #007bff;
                color: white;
                border: none;
                padding: 0.75em;
                width: 100%;
                text-align: center;
                font-size: 1em;
                border-radius: 6px;
                cursor: pointer;
                margin-bottom: 10px;
            }}
            .custom-button:hover {{
                background-color: #0056b3;
            }}
        </style>
        <form action="" method="post">
            <button class="custom-button" type="submit" name="nav_button" value="{page_name}">{label}</button>
        </form>
    """, unsafe_allow_html=True)

    if st.session_state.get("nav_button") == page_name:
        go_to(page_name)

# --- Pages ---
def welcome():
    st.title("Agricultural Advisory Tool")
    styled_button("Weather Information", "weather")
    styled_button("Crop Advice", "crop_advice")
    styled_button("Price Information", "price_info")
    styled_button("Good Agricultural Practices", "gap")
    styled_button("Notifications", "notifications")
    styled_button("Choose Version", "choose_version")

def choose_version():
    st.header("Select the Version")
    st.write(f"Current: **{st.session_state.version.replace('_', ' ').title()}**")
    if st.button("Data Saving"):
        st.session_state.version = "data_saving"
        go_back()
    if st.button("Performance Optimized"):
        st.session_state.version = "performance"
        go_back()
    if st.button("Extension Officers"):
        st.session_state.version = "extension"
        go_back()

def weather():
    st.header("Weather Information")
    st.write("This is the current weather in the Mekong Delta.")
    version = st.session_state.version
    if version == "data_saving":
        st.info("Weather graphics not available in this version.")
    elif version == "performance":
        st.image("https://example.com/performance-graph.png")
    elif version == "extension":
        st.image("https://example.com/extension-graph.png")
    styled_button("Forecasts", "weather_forecast")
    styled_button("Crop Weather Advice", "weather_crop_advice")

def weather_forecast():
    st.header("Weather Forecast")
    styled_button("Forecast for Period 1", "forecast_1")
    styled_button("Forecast for Period 2", "forecast_2")

def forecast_1():
    st.write("This is the forecast for Period 1.")
    st.image("https://via.placeholder.com/300x100")

def forecast_2():
    st.write("This is the forecast for Period 2.")
    st.image("https://via.placeholder.com/300x100")

def weather_crop_advice():
    st.header("Weather Advice for Crops")
    styled_button("Crop 1", "crop_1_weather")
    styled_button("Crop 2", "crop_2_weather")

def crop_1_weather():
    st.write("Weather advice for Crop 1")

def crop_2_weather():
    st.write("Weather advice for Crop 2")

def crop_advice():
    st.header("Crop Advice")
    styled_button("Cultivation", "cultivation")
    styled_button("Pest and Diseases", "pest_diseases")

def cultivation():
    st.write("Cultivation advice will appear here.")

def pest_diseases():
    st.write("Pest and disease control advice will appear here.")

def price_info():
    st.header("Crop Prices")
    st.write("Crop 1: $215.25")
    st.write("Crop 2: $187.50")

def gap():
    st.header("Good Agricultural Practices")
    st.markdown("""
    - Minimal soil disturbance  
    - Permanent soil cover  
    - Crop rotation
    """)
    styled_button("Step-by-Step Guide", "gap_guide")

def gap_guide():
    st.markdown("""
    1. Assess your current practices  
    2. Plan improvements  
    3. Implement changes gradually  
    4. Monitor and adjust as needed
    """)

def notifications():
    st.header("Notification Preferences")
    st.toggle("Weather Alerts")
    st.toggle("Crop Alerts")

# --- Page Map ---
PAGES = {
    "welcome": welcome,
    "choose_version": choose_version,
    "weather": weather,
    "weather_forecast": weather_forecast,
    "forecast_1": forecast_1,
    "forecast_2": forecast_2,
    "weather_crop_advice": weather_crop_advice,
    "crop_1_weather": crop_1_weather,
    "crop_2_weather": crop_2_weather,
    "crop_advice": crop_advice,
    "cultivation": cultivation,
    "pest_diseases": pest_diseases,
    "price_info": price_info,
    "gap": gap,
    "gap_guide": gap_guide,
    "notifications": notifications,
}

# --- Start the App ---
if not st.session_state.page_stack:
    st.session_state.page_stack.append("welcome")

render_page()

if len(st.session_state.page_stack) > 1:
    st.button("Back", on_click=go_back)
