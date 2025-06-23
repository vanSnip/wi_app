import streamlit as st

# --- CSS for Styled Buttons ---
st.markdown("""
    <style>
    div.stButton > button {
        width: 100%;
        background-color: #007bff;
        color: white;
        border-radius: 6px;
        padding: 0.75em 1.5em;
        font-size: 1em;
        border: none;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #0056b3;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "page_stack" not in st.session_state:
    st.session_state.page_stack = []

if "version" not in st.session_state:
    st.session_state.version = "data_saving"

if "notifications" not in st.session_state:
    st.session_state.notifications = {"weather": False, "crop": False}

# --- Navigation ---
def push_page(page_func):
    st.session_state.page_stack.append(page_func)

def go_back():
    if len(st.session_state.page_stack) > 1:
        st.session_state.page_stack.pop()

# --- Render Page ---
def render_current_page():
    current = st.session_state.page_stack[-1]
    current()
    if len(st.session_state.page_stack) > 1:
        st.button("⬅ Back", on_click=go_back)

# --- Pages ---
def welcome():
    st.title("Welcome")
    st.write("What would you like to know?")
    if st.button("Weather Information"):
        push_page(weather_info)
    if st.button("Crop Advice"):
        push_page(crop_advice)
    if st.button("Price Information"):
        push_page(price_info)
    if st.button("Good Agricultural Practices"):
        push_page(gap)
    if st.button("Notifications"):
        push_page(notifications)
    if st.button("Choose Version"):
        push_page(choose_version)

def choose_version():
    st.header("Select the Version")
    st.write(f"Current version: **{st.session_state.version.replace('_', ' ').title()}**")
    if st.button("Data Saving"):
        st.session_state.version = "data_saving"
    if st.button("Performance Optimized"):
        st.session_state.version = "performance"
    if st.button("Extension Officers"):
        st.session_state.version = "extension"

def weather_info():
    st.subheader("Weather Information")
    st.write("This is the current weather in the Mekong Delta.")

    if st.session_state.version == "data_saving":
        st.info("Weather graphics not available in this version.")
    elif st.session_state.version == "performance":
        st.image("https://example.com/performance-graph.png")
    elif st.session_state.version == "extension":
        st.image("https://example.com/extension-graph.png")

    if st.button("Forecasts"):
        push_page(weather_forecast)
    if st.button("Crop Weather Advice"):
        push_page(weather_crop_advice)

def weather_forecast():
    st.subheader("Weather Forecast")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Forecast for Period 1"):
            push_page(lambda: forecast_detail("Period 1"))
    with col2:
        if st.button("Forecast for Period 2"):
            push_page(lambda: forecast_detail("Period 2"))

def forecast_detail(period):
    st.subheader(f"Forecast for {period}")
    st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png")

def weather_crop_advice():
    st.subheader("Weather Advice")
    if st.button("Crop 1"):
        push_page(lambda: st.write("Weather advice for Crop 1"))
    if st.button("Crop 2"):
        push_page(lambda: st.write("Weather advice for Crop 2"))

def crop_advice():
    st.subheader("Crop Advice")
    if st.button("Cultivation"):
        push_page(lambda: st.write("Cultivation advice coming soon."))
    if st.button("Pest and Diseases"):
        push_page(lambda: st.write("Pest control info coming soon."))

def price_info():
    st.subheader("Crop Prices")
    st.write("Crop 1: $215.25")
    st.write("Crop 2: $187.50")

def gap():
    st.subheader("Good Agricultural Practices")
    if st.button("Conservation Agriculture"):
        push_page(lambda: st.markdown("Conservation Agriculture improves soil health and productivity."))
    if st.button("Three Principles"):
        push_page(lambda: st.markdown("- Minimal soil disturbance\n- Permanent soil cover\n- Crop rotation"))
    if st.button("Step-by-Step Guide"):
        push_page(lambda: st.markdown("1. Assess\n2. Plan\n3. Implement\n4. Monitor"))

def notifications():
    st.subheader("Notifications")
    st.checkbox("Weather Alerts", key="weather")
    st.checkbox("Crop Alerts", key="crop")
    st.write("Note: These toggles simulate preference settings.")

# --- Launch ---
if not st.session_state.page_stack:
    push_page(welcome)

render_current_page()
