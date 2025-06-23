import streamlit as st

# Initialize session state variables
if "history" not in st.session_state:
    st.session_state.history = []  # stack of steps visited

def go_to(step_func):
    """Navigate to a new step and save history."""
    st.session_state.history.append(step_func)
    step_func()

def go_back():
    """Go back to previous step if possible."""
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()  # remove current step
    st.session_state.history[-1]()  # render previous step

# --- Define your steps as functions ---

def render_welcome():
    st.title("Welcome, what would you like to know?")
    if st.button("Weather information"):
        go_to(render_weather_info)
    if st.button("Crop Advice"):
        go_to(render_crop_advice_1)
    if st.button("Price information for crops"):
        go_to(render_price_info_1)
    if st.button("Good Agricultural Practices"):
        go_to(render_gap_1)
    if st.button("Notifications"):
        go_to(render_notifications_1)
    if st.button("Version"):
        go_to(render_version_1)

def render_weather_info():
    st.header("Weather Information")
    st.write("This is the current weather in the Mekong Delta.")
    # Example buttons
    if st.button("Go to forecasts"):
        go_to(render_weather_forecasts_1)
    if st.button("Get weather advice for crops"):
        go_to(render_weather_crop_advice_1)

    if st.button("Back to previous step"):
        go_back()

def render_weather_forecasts_1():
    st.header("Weather Forecasts")
    if st.button("Forecast period 1"):
        go_to(lambda: render_weather_forecasts_2("period_1"))
    if st.button("Forecast period 2"):
        go_to(lambda: render_weather_forecasts_2("period_2"))
    if st.button("Back to previous step"):
        go_back()

def render_weather_forecasts_2(period):
    st.subheader(f"Forecast for {period}")
    st.write("Forecast details here...")
    if st.button("Back to previous step"):
        go_back()

def render_weather_crop_advice_1():
    st.header("Weather advice for crops")
    if st.button("Crop 1"):
        go_to(lambda: render_weather_crop_advice_3("crop_1"))
    if st.button("Crop 2"):
        go_to(lambda: render_weather_crop_advice_3("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def render_weather_crop_advice_3(crop):
    st.subheader(f"Advice for {crop}")
    st.write("Advice details here...")
    if st.button("Back to previous step"):
        go_back()

def render_crop_advice_1():
    st.header("For what crop do you need advice?")
    if st.button("Cultivation"):
        go_to(lambda: render_crop_advice_2("cultivation"))
    if st.button("Pest and diseases"):
        go_to(lambda: render_crop_advice_2("pest_and_diseases"))
    if st.button("Back to previous step"):
        go_back()

def render_crop_advice_2(type_):
    st.subheader(f"Advice type: {type_}")
    if type_ == "pest_and_diseases":
        if st.button("Crop 1"):
            go_to(lambda: render_pnd_1("crop_1"))
        if st.button("Crop 2"):
            go_to(lambda: render_pnd_1("crop_2"))
    else:
        if st.button("Crop 1"):
            go_to(lambda: render_crop_cultivation_adv("crop_1"))
        if st.button("Crop 2"):
            go_to(lambda: render_crop_cultivation_adv("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def render_pnd_1(crop):
    st.subheader(f"Pest and Disease advice for {crop}")
    st.write("Details here...")
    if st.button("Back to previous step"):
        go_back()

def render_crop_cultivation_adv(crop):
    st.subheader(f"Cultivation advice for {crop}")
    st.write("Details here...")
    if st.button("Back to previous step"):
        go_back()

def render_price_info_1():
    st.header("What crop do you want to know the historical prices of?")
    if st.button("Crop 1 - $215.25"):
        go_to(lambda: render_price_info_2("crop_1"))
    if st.button("Crop 2 - $187.50"):
        go_to(lambda: render_price_info_2("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def render_price_info_2(crop):
    st.subheader(f"Historical prices for {crop}")
    st.write("Price data table here...")
    if st.button("Back to previous step"):
        go_back()

def render_gap_1():
    st.header("What type of Good Agricultural Practices do you want to know about?")
    if st.button("Conservation Agriculture"):
        go_to(lambda: render_gap_2("Conservation_agriculture"))
    if st.button("3 principles of conservation agriculture"):
        go_to(lambda: render_gap_2("three_principles"))
    if st.button("Step by Step guide"):
        go_to(lambda: render_gap_2("SBS_guide"))
    if st.button("Back to previous step"):
        go_back()

def render_gap_2(type_):
    st.subheader(type_.replace("_", " ").title())
    if type_ == "Conservation_agriculture":
        st.write("Sustainable farming practices info...")
    elif type_ == "three_principles":
        st.write("""
        - Minimal soil disturbance  
        - Permanent soil cover  
        - Diversity in crop rotations
        """)
    elif type_ == "SBS_guide":
        st.write("""
        1. Assess your current practices  
        2. Plan improvements  
        3. Implement changes gradually  
        4. Monitor and adjust as needed
        """)
    if st.button("Back to previous step"):
        go_back()

def render_notifications_1():
    st.header("Notifications Settings")
    weather_status = st.session_state.get("notifications_weather", False)
    toggle_label = "Deactivate Weather Alerts" if weather_status else "Activate Weather Alerts"

    if st.button(toggle_label):
        st.session_state.notifications_weather = not weather_status
        st.experimental_rerun()  # Only here you might want to refresh UI, but can also avoid by design

    if st.button("Crop Cultivation"):
        go_to(lambda: render_notifications_2("crop_cultivation"))
    if st.button("Price Updates"):
        go_to(lambda: render_notifications_2("price_updates"))
    if st.button("Back to previous step"):
        go_back()

def render_notifications_2(type_):
    st.subheader(f"Notifications for {type_}")
    st.write("Configure notification settings here.")
    if st.button("Back to previous step"):
        go_back()

def render_version_1():
    st.header(f"Select the version you want, current: {st.session_state.get('version_show', 'Data Saving Version')}")
    if st.button("Data Saving"):
        st.session_state.version = "data_saving"
        st.session_state.version_show = "Data Saving Version"
        go_back()
    if st.button("Performance Optimized"):
        st.session_state.version = "performance"
        st.session_state.version_show = "Performance Optimized Version"
        go_back()
    if st.button("Extension Officers Version"):
        st.session_state.version = "extension"
        st.session_state.version_show = "Extension Officers Version"
        go_back()
    if st.button("Back to previous step"):
        go_back()

# Initial setup and render first step
if not st.session_state.history:
    st.session_state.history.append(render_welcome)

# Render current step
st.session_state.history[-1]()
