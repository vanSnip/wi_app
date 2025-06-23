import streamlit as st

# Initialize session state variables if they don't exist yet
if 'history' not in st.session_state:
    st.session_state.history = []
if 'version' not in st.session_state:
    st.session_state.version = "data_saving"
if 'version_show' not in st.session_state:
    st.session_state.version_show = "Data Saving Version"
if 'notifications' not in st.session_state:
    st.session_state.notifications = {'weather': False, 'crop': False}
if 'crop_prices' not in st.session_state:
    st.session_state.crop_prices = {'crop_1': 215.25, 'crop_2': 187.5}


def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()  # remove current page
        st.session_state.history.pop()  # remove previous (to re-run it freshly)
    render_current_step()


def update_step(func, *args):
    def wrapped():
        func(*args)
    st.session_state.history.append(wrapped)
    render_current_step()


def render_current_step():
    st.experimental_rerun()  # re-run app to render last step


def render_welcome():
    st.title("Decision Tree Sketch")
    st.markdown(f"### Welcome, what would you like to know?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Weather information"):
            update_step(render_weather_info)
        if st.button("Crop Advice"):
            update_step(render_crop_advice_1)
        if st.button("Price information for crops"):
            update_step(render_price_info_1)
    with col2:
        if st.button("Good Agricultural Practices"):
            update_step(render_GAP_1)
        if st.button("Notifications"):
            update_step(render_notifications_1)
        if st.button("Version"):
            update_step(render_version_1)


def render_version_1():
    st.header(f"Select the version you want (current: {st.session_state.version_show})")
    if st.button("Data Saving"):
        st.session_state.version = "data_saving"
        st.session_state.version_show = "Data Saving Version"
        st.success("Version changed to Data Saving")
    if st.button("Performance Optimised"):
        st.session_state.version = "performance"
        st.session_state.version_show = "Performance Optimised Version"
        st.success("Version changed to Performance Optimised")
    if st.button("Extension Officers Version"):
        st.session_state.version = "extension"
        st.session_state.version_show = "Extension Officers Version"
        st.success("Version changed to Extension Officers Version")

    if st.button("Back to Main Menu"):
        update_step(render_welcome)


def render_weather_info():
    st.header("Weather Information")
    st.markdown("This is the current weather in the Mekong Delta.")
    if st.session_state.version == "performance":
        st.image("https://example.com/performance-graph.png", width=300)
    elif st.session_state.version == "extension":
        st.image("https://example.com/extension-graph.png", width=300)
    else:
        st.info("Weather graphics are not available in this version to save data.")
    
    if st.button("Go to forecasts"):
        update_step(render_weather_forecasts_1)
    if st.button("Get weather advice for crops"):
        update_step(render_weather_crop_advice_1)

    if st.button("Back to Main Menu"):
        update_step(render_welcome)


def render_weather_crop_advice_1():
    st.header("For what crop do you need weather advice?")
    if st.button("Crop 1"):
        update_step(render_weather_crop_advice_3, "crop_1")
    if st.button("Crop 2"):
        update_step(render_weather_crop_advice_3, "crop_2")

    if st.button("Back"):
        go_back()


def render_weather_crop_advice_3(crop):
    st.header(f"Weather advice for {crop}")
    st.info("Here would be the advice tailored to this crop.")
    if st.button("Back"):
        go_back()


def render_weather_forecasts_1():
    st.header("Weather Forecasts")
    if st.button("Get forecast for period 1"):
        update_step(render_weather_forecasts_2, "period_1")
    if st.button("Get forecast for period 2"):
        update_step(render_weather_forecasts_2, "period_2")
    if st.button("Back"):
        go_back()


def render_weather_forecasts_2(period):
    st.header(f"Forecast for {period}")
    st.write("TEST content here.")
    st.image("https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png", width=240)
    if st.button("Back"):
        go_back()


def render_crop_advice_1():
    st.header("For what crop do you need advice?")
    if st.button("Cultivation"):
        update_step(render_crop_advice_2, "cultivation")
    if st.button("Pest and diseases"):
        update_step(render_crop_advice_2, "pest_and_diseases")
    if st.button("Back"):
        go_back()


def render_crop_advice_2(advice_type):
    if advice_type == "pest_and_diseases":
        st.header("What type of crop do you need advice for pest and disease management?")
        if st.button("Crop 1"):
            update_step(render_pnd_1, "crop_1")
        if st.button("Crop 2"):
            update_step(render_pnd_1, "crop_2")
    else:
        st.header("For what crop do you need cultivation advice?")
        if st.button("Crop 1"):
            update_step(render_crop_cultivation_adv, "crop_1")
        if st.button("Crop 2"):
            update_step(render_crop_cultivation_adv, "crop_2")

    if st.button("Back"):
        go_back()


def render_pnd_1(crop):
    st.header(f"Pest and Disease advice for {crop}")
    st.info("Advice would be shown here.")
    if st.button("Back"):
        go_back()


def render_crop_cultivation_adv(crop):
    st.header(f"Cultivation advice for {crop}")
    st.info("Advice would be shown here.")
    if st.button("Back"):
        go_back()


def render_price_info_1():
    st.header("What crop do you want to know the historical prices of?")
    cp = st.session_state.crop_prices
    if st.button(f"Crop 1 - ${cp['crop_1']:.2f}"):
        update_step(render_price_info_2, "crop_1")
    if st.button(f"Crop 2 - ${cp['crop_2']:.2f}"):
        update_step(render_price_info_2, "crop_2")
    if st.button("Back to Main Menu"):
        update_step(render_welcome)


def render_price_info_2(crop):
    st.header(f"Historical price data for {crop}")
    st.write("Table and location info would be inserted here.")
    if st.button("Back"):
        go_back()


def render_GAP_1():
    st.header("What type of Good Agricultural Practices do you want to know about?")
    if st.button("Conservation Agriculture"):
        update_step(render_GAP_2, "Conservation_agriculture")
    if st.button("3 principles of conservation agriculture"):
        update_step(render_GAP_2, "three_principles")
    if st.button("Step by Step guide"):
        update_step(render_GAP_2, "SBS_guide")
    if st.button("Back to Main Menu"):
        update_step(render_welcome)


def render_GAP_2(topic):
    if topic == "Conservation_agriculture":
        st.header("Conservation Agriculture")
        st.write("Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.")
    elif topic == "three_principles":
        st.header("The three principles of conservation agriculture are:")
        st.markdown("""
        - Minimal soil disturbance  
        - Permanent soil cover  
        - Diversity in crop rotations
        """)
    elif topic == "SBS_guide":
        st.header("Step by Step guide to implementing Good Agricultural Practices:")
        st.markdown("""
        1. Assess your current practices  
        2. Plan improvements  
        3. Implement changes gradually  
        4. Monitor and adjust as needed
        """)
    if st.button("Back"):
        go_back()


def render_notifications_1():
    st.header("What type of notifications would you like to receive?")
    weather_enabled = st.session_state.notifications['weather']
    weather_label = "Deactivate Weather Alerts" if weather_enabled else "Activate Weather Alerts"

    if st.button(weather_label):
        st.session_state.notifications['weather'] = not weather_enabled
        msg = "Weather alerts activated." if st.session_state.notifications['weather'] else "Weather alerts deactivated."
        st.success(msg)

    if st.button("Crop Cultivation"):
        update_step(render_notifications_2, "crop_cultivation")
    if st.button("Price Updates"):
        update_step(render_notifications_2, "price_updates")
    if st.button("Back to Main Menu"):
        update_step(render_welcome)


def render_notifications_2(notif_type):
    if notif_type == "crop_cultivation":
        st.header("Toggle notifications for crops")
        if st.button("For crop 1"):
            st.success("Crop 1 notifications activated (placeholder)")
        if st.button("For crop 2"):
            st.success("Crop 2 notifications activated (placeholder)")
    elif notif_type == "price_updates":
        st.header("What crop price updates would you like to receive?")
        if st.button("About crop 1"):
            st.success("Price updates for crop 1 activated (placeholder)")
        if st.button("About crop 2"):
            st.success("Price updates for crop 2 activated (placeholder)")

    if st.button("Back"):
        go_back()


# Main app controller
if 'history' not in st.session_state or len(st.session_state.history) == 0:
    st.session_state.history = [render_welcome]

# Run the last step function in history
st.session_state.history[-1]()
