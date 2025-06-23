import streamlit as st

# Styles for blue buttons and back buttons
button_css = """
<style>
div.stButton > button {
    background-color: #007bff;
    color: white;
    border-radius: 5px;
    padding: 0.5em 1.2em;
    font-size: 1em;
    border: none;
    cursor: pointer;
    margin: 0.5em 0;
}
div.stButton > button:hover {
    background-color: #0056b3;
}
div.back-button > button {
    background-color: #6c757d !important;
}
div.back-button > button:hover {
    background-color: #5a6268 !important;
}
</style>
"""

st.markdown(button_css, unsafe_allow_html=True)

# Initialize session state variables
if "history" not in st.session_state:
    st.session_state.history = []  # Stack of screen function names
if "version" not in st.session_state:
    st.session_state.version = "data_saving"
if "version_show" not in st.session_state:
    st.session_state.version_show = "Data Saving Version"
if "notifications" not in st.session_state:
    st.session_state.notifications = {
        "weather": False,
        "crop": False,
    }

# Crop prices example
cropPrices = {
    "crop_1": 215.25,
    "crop_2": 187.5,
}

# Helper to push new screen to history and update
def navigate(screen_name, param=None):
    # Add the screen to history, with optional param as tuple (screen_name, param)
    if param:
        st.session_state.history.append((screen_name, param))
    else:
        st.session_state.history.append((screen_name, None))

# Helper to go back in history
def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()

# Helper to get current screen
def current_screen():
    if len(st.session_state.history) == 0:
        return ("welcome", None)
    return st.session_state.history[-1]

# Screen functions below (each takes param or None)


def render_welcome(_=None):
    st.header("Welcome, what would you like to know?")
    if st.button("Weather information"):
        navigate("weather_info")
    if st.button("Crop Advice"):
        navigate("crop_advice_1")
    if st.button("Price information for crops"):
        navigate("price_info_1")
    if st.button("Good Agricultural Practices"):
        navigate("GAP_1")
    if st.button("Notifications"):
        navigate("notifications_1")
    if st.button("Version"):
        navigate("version_1")
    # No back button on welcome


def render_version_1(_=None):
    st.header(f"Select the version you want (current: {st.session_state.version_show})")

    if st.button("Data Saving"):
        st.session_state.version = "data_saving"
        st.session_state.version_show = "Data Saving Version"
        st.experimental_rerun()
    if st.button("Performance Optimised"):
        st.session_state.version = "performance"
        st.session_state.version_show = "Performance Optimised Version"
        st.experimental_rerun()
    if st.button("Extension Officers Version"):
        st.session_state.version = "extension"
        st.session_state.version_show = "Extension Officers Version"
        st.experimental_rerun()
    if st.button("Go back to main menu", key="back_version_main"):
        go_back()


def render_weather_info(_=None):
    st.header("Weather Information")

    version = st.session_state.version
    if version == "performance":
        st.image("https://example.com/performance-graph.png", width=400)
    elif version == "extension":
        st.image("https://example.com/extension-graph.png", width=400)
    else:
        st.write("Weather graphics are not available in this version to save data.")

    if st.button("Go to forecasts"):
        navigate("weather_forecasts_1")
    if st.button("Get weather advice for crops"):
        navigate("weather_crop_advice_1")

    back_button()


def render_weather_crop_advice_1(_=None):
    st.header("For what crop do you need weather advice?")
    if st.button("crop 1"):
        navigate("weather_crop_advice_3", "crop_1")
    if st.button("crop 2"):
        navigate("weather_crop_advice_3", "crop_2")

    back_button()


def render_weather_forecasts_1(_=None):
    st.header("Weather Forecasts")

    if st.button("Get forecast for period 1"):
        navigate("weather_forecasts_2", "period_1")
    if st.button("Get forecast for period 2"):
        navigate("weather_forecasts_2", "period_2")

    back_button()


def render_weather_forecasts_2(period):
    st.header(f"Forecast for {period}")

    st.write("TEST")
    st.image(
        "https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png",
        width=250,
    )

    back_button()


def render_crop_advice_1(_=None):
    st.header("For what crop do you need advice?")
    if st.button("Cultivation"):
        navigate("crop_advice_2", "cultivation")
    if st.button("Pest and diseases"):
        navigate("crop_advice_2", "pest_and_diseases")

    back_button()


def render_crop_advice_2(type_):
    st.header(f"Advice type: {type_}")
    if type_ == "pest_and_diseases":
        st.write("What type of crop do you need advice for pest and disease management?")
        if st.button("crop_1"):
            navigate("pnd_1", "crop_1")
        if st.button("crop_2"):
            navigate("pnd_1", "crop_2")
    else:
        st.write("For what crop do you need advice?")
        if st.button("crop_1"):
            navigate("crop_cultivation_adv", "crop_1")
        if st.button("crop_2"):
            navigate("crop_cultivation_adv", "crop_2")

    back_button()


def render_price_info_1(_=None):
    st.header("What crop do you want to know the historical prices of?")
    if st.button(f"crop_1 - ${cropPrices['crop_1']:.2f}"):
        navigate("price_info_2", "crop_1")
    if st.button(f"crop_2 - ${cropPrices['crop_2']:.2f}"):
        navigate("price_info_2", "crop_2")

    back_button()


def render_price_info_2(crop):
    st.header(f"Historical Price Data for {crop}")
    st.write("Here is the historical price data for", crop)
    st.write("{Insert table} and it is sold at {insert location}")

    back_button()


def render_GAP_1(_=None):
    st.header("What type of Good Agricultural Practices do you want to know about?")
    if st.button("Conservation Agriculture"):
        navigate("GAP_2", "Conservation_agriculture")
    if st.button("3 principles of conservation agriculture"):
        navigate("GAP_2", "three_principles")
    if st.button("Step by Step guide"):
        navigate("GAP_2", "SBS_guide")

    back_button()


def render_GAP_2(type_):
    st.header(f"GAP: {type_}")
    if type_ == "Conservation_agriculture":
        st.write("Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.")
    elif type_ == "three_principles":
        st.write(
            """
            The three principles of conservation agriculture are:
            - Minimal soil disturbance
            - Permanent soil cover
            - Diversity in crop rotations
            """
        )
    elif type_ == "SBS_guide":
        st.write(
            """
            Step by Step guide to implementing Good Agricultural Practices:
            1. Assess your current practices
            2. Plan improvements
            3. Implement changes gradually
            4. Monitor and adjust as needed
            """
        )

    back_button()


def render_notifications_1(_=None):
    st.header("What type of notifications would you like to receive?")

    weather_label = (
        "Deactivate Weather Alerts" if st.session_state.notifications["weather"] else "Activate Weather Alerts"
    )

    if st.button(weather_label):
        st.session_state.notifications["weather"] = not st.session_state.notifications["weather"]
        # After toggling, just refresh current screen (don't push new to history)
        return

    if st.button("Crop Cultivation"):
        navigate("notifications_2", "crop_cultivation")
    if st.button("Price Updates"):
        navigate("notifications_2", "price_updates")

    if st.button("To begin"):
        st.session_state.history = []
        # Goes back to welcome automatically
        return

    back_button()


def render_notifications_2(type_):
    st.header("Notifications: " + type_)

    if type_ == "crop_cultivation":
        st.write("Toggle notifications for crops")
        if st.button("For crop 1"):
            st.session_state.notifications["crop"] = True
            st.success("Notifications for crop 1 activated.")
        if st.button("For crop 2"):
            st.session_state.notifications["crop"] = True
            st.success("Notifications for crop 2 activated.")
    elif type_ == "price_updates":
        st.write("What crop price updates would you like to receive?")
        if st.button("About crop 1"):
            st.success("Price update notifications for crop 1 activated.")
        if st.button("About crop 2"):
            st.success("Price update notifications for crop 2 activated.")

    back_button()


# Back button for screens except welcome
def back_button():
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Back to previous step", key="back"):
            go_back()


# Map screen name to functions
screen_funcs = {
    "welcome": render_welcome,
    "version_1": render_version_1,
    "weather_info": render_weather_info,
    "weather_crop_advice_1": render_weather_crop_advice_1,
    "weather_forecasts_1": render_weather_forecasts_1,
    "weather_forecasts_2": render_weather_forecasts_2,
    "crop_advice_1": render_crop_advice_1,
    "crop_advice_2": render_crop_advice_2,
    "price_info_1": render_price_info_1,
    "price_info_2": render_price_info_2,
    "GAP_1": render_GAP_1,
    "GAP_2": render_GAP_2,
    "notifications_1": render_notifications_1,
    "notifications_2": render_notifications_2,
    # Add placeholder for others you want
    # "pnd_1": render_pnd_1,
    # "crop_cultivation_adv": render_crop_cultivation_adv,
}

# If no history, start with welcome
if not st.session_state.history:
    st.session_state.history.append(("welcome", None))

# Get current screen from stack
screen, param = current_screen()

# Render current screen
if screen in screen_funcs:
    screen_funcs[screen](param)
else:
    st.error(f"Screen {screen} not implemented.")
