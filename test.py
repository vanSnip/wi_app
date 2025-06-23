import streamlit as st

# Initialize all session_state keys upfront to avoid AttributeErrors
if "history" not in st.session_state:
    st.session_state.history = []
if "notifications_weather" not in st.session_state:
    st.session_state.notifications_weather = False
if "notifications_crop_1" not in st.session_state:
    st.session_state.notifications_crop_1 = False
if "notifications_crop_2" not in st.session_state:
    st.session_state.notifications_crop_2 = False
if "notifications_price_crop_1" not in st.session_state:
    st.session_state.notifications_price_crop_1 = False
if "notifications_price_crop_2" not in st.session_state:
    st.session_state.notifications_price_crop_2 = False
if "version" not in st.session_state:
    st.session_state.version = "data_saving"
if "version_show" not in st.session_state:
    st.session_state.version_show = "Data Saving Version"

# For locking branches, not strictly needed, but let's keep it consistent
if "branch_locked" not in st.session_state:
    st.session_state.branch_locked = False

# Crop prices dictionary
crop_prices = {
    "crop_1": 215.25,
    "crop_2": 187.5,
}

def update_step(func):
    st.session_state.history.append(func)
    func()

def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()
        previous = st.session_state.history[-1]
        previous()

def render_with_back(question_text, options_html, show_back=True):
    st.markdown(f"### {question_text}")
    # Display the buttons or options (passed as HTML string)
    # Streamlit doesn't render raw HTML buttons with JS, so we convert to streamlit buttons here
    # For this example, I'll keep the logic using Streamlit buttons instead of raw HTML
    
    # We cannot directly use the HTML buttons from your original JS in Streamlit,
    # so instead, render the question text and buttons in functions
    
    # This function will be used mostly internally — see below for the correct way to show buttons
    
    # We'll manage navigation in the main render functions instead.
    pass

def render_welcome():
    st.session_state.branch_locked = False
    st.title("Decision Tree Sketch")
    st.markdown("Welcome, what would you like to know?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Weather information"):
            update_step(lambda: weather_info_1(st.session_state.version))
        if st.button("Crop Advice"):
            update_step(crop_advice_1)
        if st.button("Price information for crops"):
            update_step(Price_info_1)
    with col2:
        if st.button("Good Agricultural Practices"):
            update_step(GAP_1)
        if st.button("Notifications"):
            update_step(Notifications_1)
        if st.button("Version"):
            update_step(Version_1)

def Version_1():
    st.session_state.branch_locked = True
    st.markdown(f"Select the version you want, the current version is the **{st.session_state.version_show}**")
    if st.button("Data Saving"):
        update_step(data_saving_version)
    if st.button("Performance Optimised"):
        update_step(performance_optimized_version)
    if st.button("Version for Extension Officers"):
        update_step(extension_officer_version)
    if st.button("Go back to main menu"):
        update_step(render_welcome)
    if st.button("Back to previous step"):
        go_back()

def extension_officer_version():
    st.session_state.version = "extension"
    st.session_state.version_show = "Extension Officers Version"
    st.markdown("Extension Officers Version")
    st.write("This version includes tools and insights for agricultural extension services.")
    if st.button("Go back to main menu"):
        update_step(render_welcome)
    if st.button("Back to previous step"):
        go_back()

def data_saving_version():
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"
    st.markdown("Data Saving Version")
    st.write("This version is optimized for low data usage.")
    if st.button("Go back to main menu"):
        update_step(render_welcome)
    if st.button("Back to previous step"):
        go_back()

def performance_optimized_version():
    st.session_state.version = "performance"
    st.session_state.version_show = "Performance Optimised Version"
    st.markdown("Performance Optimised Version")
    st.write("This version prioritizes speed and performance for low-end devices.")
    if st.button("Go back to main menu"):
        update_step(render_welcome)
    if st.button("Back to previous step"):
        go_back()

def weather_info_1(version):
    st.session_state.branch_locked = True
    st.markdown("Weather Information")
    if version == "performance":
        st.image("https://example.com/performance-graph.png", use_column_width=True)
    elif version == "extension":
        st.image("https://example.com/extension-graph.png", use_column_width=True)
    else:
        st.write("Weather graphics are not available in this version to save data.")
    if st.button("Go to forecasts"):
        update_step(weather_forecasts_1)
    if st.button("Get weather advice for crops"):
        update_step(weather_crop_advice_1)
    if st.button("Back to previous step"):
        go_back()

def weather_crop_advice_1():
    st.session_state.branch_locked = True
    st.markdown("For what crop do you need weather advice?")
    if st.button("Crop 1"):
        update_step(lambda: weather_crop_advice_3("crop_1"))
    if st.button("Crop 2"):
        update_step(lambda: weather_crop_advice_3("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def weather_crop_advice_3(crop):
    st.markdown(f"Weather advice for {crop}")
    st.write("... Insert weather advice details here ...")
    if st.button("Back to previous step"):
        go_back()

def weather_forecasts_1():
    st.session_state.branch_locked = True
    st.markdown("This is the weather forecast {Insert uploaded graph}")
    if st.button("Get forecast for period 1"):
        update_step(lambda: weather_forecasts_2("period_1"))
    if st.button("Get forecast for period 2"):
        update_step(lambda: weather_forecasts_2("period_2"))
    if st.button("Back to previous step"):
        go_back()

def weather_forecasts_2(period):
    st.session_state.branch_locked = True
    if period == "period_1":
        st.markdown("This is the forecast for period 1")
        st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png", width=300)
    elif period == "period_2":
        st.markdown("This is the forecast for period 2")
        st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png", width=300)
    if st.button("Back to previous step"):
        go_back()

def crop_advice_1():
    st.session_state.branch_locked = True
    st.markdown("For what crop do you need advice?")
    if st.button("Cultivation"):
        update_step(lambda: crop_advice_2("cultivation"))
    if st.button("Pest and diseases"):
        update_step(lambda: crop_advice_2("pest_and_diseases"))
    if st.button("Back to previous step"):
        go_back()

def crop_advice_2(type_):
    st.session_state.branch_locked = True
    if type_ == "pest_and_diseases":
        st.markdown("What type of crop do you need advice for pest and disease management?")
        if st.button("Crop 1"):
            update_step(lambda: pnd_1("crop_1"))
        if st.button("Crop 2"):
            update_step(lambda: pnd_1("crop_2"))
    else:
        st.markdown("For what crop do you need advice?")
        if st.button("Crop 1"):
            update_step(lambda: crop_cultivation_adv("crop_1"))
        if st.button("Crop 2"):
            update_step(lambda: crop_cultivation_adv("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def pnd_1(crop):
    st.markdown(f"Pest and disease advice for {crop}")
    st.write("... Insert detailed pest and disease advice here ...")
    if st.button("Back to previous step"):
        go_back()

def crop_cultivation_adv(crop):
    st.markdown(f"Cultivation advice for {crop}")
    st.write("... Insert detailed cultivation advice here ...")
    if st.button("Back to previous step"):
        go_back()

def Price_info_1():
    st.session_state.branch_locked = True
    st.markdown("What crop do you want to know the historical prices of?")
    if st.button(f"Crop 1 - ${crop_prices['crop_1']:.2f}"):
        update_step(lambda: price_info_2("crop_1"))
    if st.button(f"Crop 2 - ${crop_prices['crop_2']:.2f}"):
        update_step(lambda: price_info_2("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def price_info_2(crop):
    st.session_state.branch_locked = True
    st.markdown(f"Here is the historical price data for {crop}:")
    st.write("{Insert table} and it is sold at {insert location}")
    if st.button("Back to previous step"):
        go_back()

def GAP_1():
    st.session_state.branch_locked = True
    st.markdown("What type of Good Agricultural Practices do you want to know about?")
    if st.button("Conservation Agriculture"):
        update_step(lambda: GAP_2("Conservation_agriculture"))
    if st.button("3 principles of conservation agriculture"):
        update_step(lambda: GAP_2("three_principles"))
    if st.button("Step by Step guide"):
        update_step(lambda: GAP_2("SBS_guide"))
    if st.button("Back to previous step"):
        go_back()

def GAP_2(type_):
    st.session_state.branch_locked = True
    if type_ == "Conservation_agriculture":
        st.markdown("Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.")
    elif type_ == "three_principles":
        st.markdown("""
        The three principles of conservation agriculture are:
        - Minimal soil disturbance
        - Permanent soil cover
        - Diversity in crop rotations
        """)
    elif type_ == "SBS_guide":
        st.markdown("""
        Step by Step guide to implementing Good Agricultural Practices:
        1. Assess your current practices
        2. Plan improvements
        3. Implement changes gradually
        4. Monitor and adjust as needed
        """)
    if st.button("Back to previous step"):
        go_back()

def Notifications_1():
    st.session_state.branch_locked = True
    weather_label = "Deactivate Weather Alerts" if st.session_state.notifications_weather else "Activate Weather Alerts"
    st.markdown("What type of notifications would you like to receive?")
    if st.button(weather_label):
        update_step(activate_weather_alerts)
    if st.button("Crop Cultivation"):
        update_step(lambda: Notifications_2("crop_cultivation"))
    if st.button("Price Updates"):
        update_step(lambda: Notifications_2("price_updates"))
    if st.button("To begin"):
        st.experimental_rerun()

def Notifications_2(type_):
    st.session_state.branch_locked = True
    if type_ == "weather_alerts":
        st.session_state.notifications_weather = True
        st.markdown(f"You will receive weather alerts for severe conditions. Weather alerts: {'Active' if st.session_state.notifications_weather else 'Inactive'}")
        if st.button("Activate Weather Alerts"):
            update_step(activate_weather_alerts)
    elif type_ == "crop_cultivation":
        st.markdown("Toggle notifications for crops")
        if st.button("For crop 1"):
            update_step(lambda: activate_crop_alerts("crop_1"))
        if st.button("For crop 2"):
            update_step(lambda: activate_crop_alerts("crop_2"))
    elif type_ == "price_updates":
        st.markdown("What crop price updates would you like to receive?")
        if st.button("About crop 1"):
            update_step(lambda: activate_price_alerts("crop_1"))
        if st.button("About crop 2"):
            update_step(lambda: activate_price_alerts("crop_2"))
    if st.button("Back to previous step"):
        go_back()

def activate_weather_alerts():
    st.session_state.branch_locked = True
    st.session_state.notifications_weather = not st.session_state.notifications_weather
    if st.session_state.notifications_weather:
        st.markdown("Weather alerts activated. You will now receive notifications for severe weather conditions.")
    else:
        st.markdown("Weather alerts deactivated. You will no longer receive weather notifications.")
    label = "Deactivate Weather Alerts" if st.session_state.notifications_weather else "Activate Weather Alerts"
    if st.button(label):
        update_step(activate_weather_alerts)
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

def activate_crop_alerts(crop):
    key = f"notifications_{crop}"
    st.session_state[key] = not st.session_state.get(key, False)
    status = "activated" if st.session_state[key] else "deactivated"
    st.markdown(f"Notifications for {crop} {status}.")
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

def activate_price_alerts(crop):
    key = f"notifications_price_{crop}"
    st.session_state[key] = not st.session_state.get(key, False)
    status = "activated" if st.session_state[key] else "deactivated"
    st.markdown(f"Price notifications for {crop} {status}.")
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

# Entry point
if "history" not
