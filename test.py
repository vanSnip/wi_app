import streamlit as st

def styled_button(label, key=None):
    button_html = f"""
    <style>
        .custom-button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 0.75em 1.5em;
            width: 100%;
            text-align: center;
            font-size: 1em;
            border-radius: 6px;
            cursor: pointer;
        }}
        .custom-button:hover {{
            background-color: #0056b3;
        }}
        .button-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }}
    </style>
    <div class="button-container">
        <form action="" method="post">
            <button class="custom-button" name="custom_button" type="submit">{label}</button>
        </form>
    </div>
    """
    return st.markdown(button_html, unsafe_allow_html=True)

if "button_pressed" not in st.session_state:
    st.session_state.button_pressed = None

def render_menu():
    st.subheader("Main Menu")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🌦 Weather", key="weather"):
            st.session_state.button_pressed = "weather"
    with col2:
        if st.button("💲 Price Info", key="price"):
            st.session_state.button_pressed = "price"

    if st.session_state.button_pressed == "weather":
        st.write("You chose weather!")
    elif st.session_state.button_pressed == "price":
        st.write("You chose price info.")

# Initialize session state for navigation and version
if "page_stack" not in st.session_state:
    st.session_state.page_stack = []
if "version" not in st.session_state:
    st.session_state.version = "data_saving"
if "notifications" not in st.session_state:
    st.session_state.notifications = {
        "weather": False,
        "crop": False
    }

# Define navigation
def go_to(page_func):
    st.session_state.page_stack.append(page_func)
    st.experimental_rerun()

def go_back():
    if len(st.session_state.page_stack) > 1:
        st.session_state.page_stack.pop()
        st.experimental_rerun()

# UI with back button
def render_page(func):
    func()
    if len(st.session_state.page_stack) > 1:
        st.button("Back", on_click=go_back)

# --- Pages ---
def welcome():
    st.title("Welcome")
    st.write("What would you like to know?")
    st.button("Weather Information", on_click=lambda: go_to(weather_info))
    st.button("Crop Advice", on_click=lambda: go_to(crop_advice))
    st.button("Price Information", on_click=lambda: go_to(price_info))
    st.button("Good Agricultural Practices", on_click=lambda: go_to(gap))
    st.button("Notifications", on_click=lambda: go_to(notifications))
    st.button("Choose Version _test", on_click=lambda: go_to(choose_version))

def choose_version():
    st.header("Select the Version")
    st.write(f"Current: **{st.session_state.version.replace('_', ' ').title()}**")
    st.button("Data Saving", on_click=lambda: set_version("data_saving"))
    st.button("Performance Optimized", on_click=lambda: set_version("performance"))
    st.button("Extension Officers", on_click=lambda: set_version("extension"))

def set_version(v):
    st.session_state.version = v
    go_back()

def weather_info():
    st.subheader("Weather Information")
    st.write("This is the current weather in the Mekong Delta.")

    if st.session_state.version == "data_saving":
        st.info("Weather graphics not available in this version.")
    elif st.session_state.version == "performance":
        st.image("https://example.com/performance-graph.png")
    elif st.session_state.version == "extension":
        st.image("https://example.com/extension-graph.png")

    st.button("Forecasts", on_click=lambda: go_to(weather_forecast))
    st.button("Crop Weather Advice", on_click=lambda: go_to(weather_crop_advice))

def weather_forecast():
    st.subheader("Weather Forecast")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Forecast for Period 1", on_click=lambda: go_to(lambda: forecast_detail("Period 1")))
    with col2:
        st.button("Forecast for Period 2", on_click=lambda: go_to(lambda: forecast_detail("Period 2")))

def forecast_detail(period):
    st.write(f"This is the forecast for {period}.")
    st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png")

def weather_crop_advice():
    st.subheader("Weather Advice")
    st.button("Crop 1", on_click=lambda: go_to(lambda: st.write("Weather advice for Crop 1")))
    st.button("Crop 2", on_click=lambda: go_to(lambda: st.write("Weather advice for Crop 2")))

def crop_advice():
    st.subheader("Crop Advice")
    st.button("Cultivation", on_click=lambda: go_to(lambda: st.write("Cultivation advice coming soon.")))
    st.button("Pest and Diseases", on_click=lambda: go_to(lambda: st.write("Pest control info coming soon.")))

def price_info():
    st.subheader("Crop Prices")
    st.write("Crop 1: $215.25")
    st.write("Crop 2: $187.50")

def gap():
    st.subheader("Good Agricultural Practices")
    st.button("Conservation Agriculture", on_click=lambda: go_to(lambda: st.markdown("""
        Conservation Agriculture improves soil health and productivity.
    """)))
    st.button("Three Principles", on_click=lambda: go_to(lambda: st.markdown("""
        - Minimal soil disturbance  
        - Permanent soil cover  
        - Crop rotation  
    """)))
    st.button("Step-by-Step Guide", on_click=lambda: go_to(lambda: st.markdown("""
        1. Assess  
        2. Plan  
        3. Implement  
        4. Monitor  
    """)))

def notifications():
    st.subheader("Notifications")
    st.toggle("Weather Alerts", key="weather_alerts")
    st.toggle("Crop Alerts", key="crop_alerts")
    st.write("Note: These toggles simulate preference settings.")

# --- Launch app ---
if not st.session_state.page_stack:
    st.session_state.page_stack.append(welcome)

render_page(st.session_state.page_stack[-1])
