import streamlit as st

# Set page config
st.set_page_config(page_title="Decision Tree Sketch")

# CSS for blue buttons & styling
st.markdown("""
    <style>
    .stButton > button {
        background-color: #007bff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5em 1.2em;
        font-size: 1em;
        cursor: pointer;
        margin: 0.5em;
        width: 200px;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .back-button > button {
        background-color: #6c757d !important;
        margin-top: 1em;
        width: auto;
    }
    .back-button > button:hover {
        background-color: #5a6268 !important;
    }
    .options {
        display: flex;
        flex-direction: column;
        gap: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for history stack and other variables
if 'history_stack' not in st.session_state:
    st.session_state.history_stack = []
if 'branch_locked' not in st.session_state:
    st.session_state.branch_locked = False
if 'notifications_enabled' not in st.session_state:
    st.session_state.notifications_enabled = {'weather': False, 'crop': False}
if 'version' not in st.session_state:
    st.session_state.version = "data_saving"
if 'version_show' not in st.session_state:
    st.session_state.version_show = "Data Saving Version"
if 'crop_prices' not in st.session_state:
    st.session_state.crop_prices = {'crop_1': 215.25, 'crop_2': 187.5}

# Helper: push new screen function to history and render it
def update_step(func):
    st.session_state.history_stack.append(func)
    func()

# Helper: go back one step
def go_back():
    if len(st.session_state.history_stack) > 1:
        st.session_state.history_stack.pop()
    st.session_state.history_stack[-1]()

# Helper: render question and options with back button if desired
def render_with_back(question_text, options_funcs, show_back=True):
    st.markdown(f"### {question_text}")
    for text, func in options_funcs:
        if st.button(text):
            update_step(func)
            st.experimental_rerun()  # Force rerun on button click to re-render new screen
    if show_back and len(st.session_state.history_stack) > 1:
        if st.button("Back to previous step"):
            go_back()
            st.experimental_rerun()

# --- Screens definitions ---
def render_welcome():
    question = "Welcome, what would you like to know?"
    options = [
        ("Weather information", lambda: Weather_info_1(st.session_state.version)),
        ("Crop Advice", crop_advice_1),
        ("Price information for crops", Price_info_1),
        ("Good Agricultural Practices", GAP_1),
        ("Notifications", Notifications_1),
        ("Version", Version_1),
    ]
    render_with_back(question, options, show_back=False)

def Version_1():
    question = f"Select the version you want, the current version is the {st.session_state.version_show}"
    options = [
        ("Data Saving", data_saving_version),
        ("Performance Optimised", performance_optimized_version),
        ("Version for Extension Officers", extension_officer_version),
        ("Go back to main menu", render_welcome),
    ]
    render_with_back(question, options, show_back=False)

def extension_officer_version():
    st.session_state.version = "extension"
    st.session_state.version_show = "Extension Officers Version"
    question = "Extension Officers Version"
    st.markdown("<p>This version includes tools and insights for agricultural extension services.</p>", unsafe_allow_html=True)
    options = [
        ("Go back to main menu", render_welcome)
    ]
    render_with_back(question, options, show_back=False)

def data_saving_version():
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"
    question = "Data Saving Version"
    st.markdown("<p>This version is optimized for low data usage.</p>", unsafe_allow_html=True)
    options = [
        ("Go back to main menu", render_welcome)
    ]
    render_with_back(question, options, show_back=False)

def performance_optimized_version():
    st.session_state.version = "performance"
    st.session_state.version_show = "Performance Optimised Version"
    question = "Performance Optimised Version"
    st.markdown("<p>This version prioritizes speed and performance for low-end devices.</p>", unsafe_allow_html=True)
    options = [
        ("Go back to main menu", render_welcome)
    ]
    render_with_back(question, options, show_back=False)

def Weather_info_1(version):
    question = "Weather Information"
    image_html = ""
    if version == "performance":
        image_html = '<img src="https://example.com/performance-graph.png" alt="Performance Graph" style="max-width:60%; height:auto;">'
    elif version == "extension":
        image_html = '<img src="https://example.com/extension-graph.png" alt="Extension Graph" style="max-width:60%; height:auto;">'
    else:
        image_html = "<p>Weather graphics are not available in this version to save data.</p>"
    st.markdown("<p>This is the current weather in the Mekong Delta.</p>" + image_html, unsafe_allow_html=True)
    options = [
        ("Go to forecasts", Weather_forecasts_1),
        ("Get weather advice for crops", weather_crop_advice_1)
    ]
    render_with_back(question, options)

def weather_crop_advice_1():
    question = "For what crop do you need weather advice?"
    options = [
        ("crop 1", lambda: weather_crop_advice_3('crop_1')),
        ("crop 2", lambda: weather_crop_advice_3('crop_2'))
    ]
    render_with_back(question, options)

def weather_crop_advice_3(crop):
    st.markdown(f"<p>Weather advice for {crop}</p>", unsafe_allow_html=True)
    if st.button("Back to weather advice menu"):
        update_step(weather_crop_advice_1)
        st.experimental_rerun()
    if st.button("Back to main menu"):
        st.session_state.history_stack = [render_welcome]
        render_welcome()
        st.experimental_rerun()

def Weather_forecasts_1():
    question = "This is the weather forecast {Insert uploaded graph}"
    options = [
        ("Get forecast for period {1}", lambda: weather_forecasts_2('period_1')),
        ("Get forecast for period {2}", lambda: weather_forecasts_2('period_2'))
    ]
    render_with_back(question, options)

def weather_forecasts_2(period):
    if period == "period_1":
        message = """
        <p>This is the forecast for period {2}</p>
        <p> TEST </p>
        <img src="https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png" alt="Example image" style="max-width:40%; height:auto;">
        """
    else:
        message = """
        <p>This is the forecast for period {1}</p>
        <p> TEST </p>
        <img src="https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png" alt="Example image" style="max-width:40%; height:auto;">
        """
    st.markdown(message, unsafe_allow_html=True)
    if st.button("Back to forecasts"):
        update_step(Weather_forecasts_1)
        st.experimental_rerun()

def crop_advice_1():
    question = "For what crop do you need advice?"
    options = [
        ("Cultivation", lambda: crop_advice_2('cultivation')),
        ("Pest and diseases", lambda: crop_advice_2('pest_and_diseases'))
    ]
    render_with_back(question, options)

def crop_advice_2(type_):
    if type_ == "pest_and_diseases":
        question = "What type of crop do you need advice for pest and disease management?"
        options = [
            ("crop_1", lambda: pnd_1('crop_1')),
            ("crop_2", lambda: pnd_1('crop_2'))
        ]
    else:
        question = "For what crop do you need advice?"
        options = [
            ("crop_1", lambda: crop_cultivation_adv('crop_1')),
            ("crop_2", lambda: crop_cultivation_adv('crop_2'))
        ]
    render_with_back(question, options)

def pnd_1(crop):
    st.markdown(f"<p>Pest and disease advice for {crop}</p>", unsafe_allow_html=True)
    if st.button("Back to crop advice"):
        update_step(crop_advice_1)
        st.experimental_rerun()

def crop_cultivation_adv(crop):
    st.markdown(f"<p>Cultivation advice for {crop}</p>", unsafe_allow_html=True)
    if st.button("Back to crop advice"):
        update_step(crop_advice_1)
        st.experimental_rerun()

def Price_info_1():
    cp = st.session_state.crop_prices
    question = "What crop do you want to know the historical prices of?"
    options = [
        (f"crop_1 - ${cp['crop_1']:.2f}", lambda: price_info_2('crop_1')),
        (f"crop_2 - ${cp['crop_2']:.2f}", lambda: price_info_2('crop_2'))
    ]
    render_with_back(question, options)

def price_info_2(crop):
    st.markdown(f"<p>Here is the historical price data for {crop}:</p><p>{{Insert table}} and it is sold at {{insert location}}</p>", unsafe_allow_html=True)
    if st.button("Back to price info"):
        update_step(Price_info_1)
        st.experimental_rerun()

def GAP_1():
    question = "What type of Good Agricultural Practices do you want to know about?"
    options = [
        ("Conservation Agriculture", lambda: GAP_2('Conservation_agriculture')),
        ("3 principles of conservation agriculture", lambda: GAP_2('three_principles')),
        ("Step by Step guide", lambda: GAP_2('SBS_guide'))
    ]
    render_with_back(question, options)

def GAP_2(type_):
    if type_ == "Conservation_agriculture":
        st.markdown("<p>Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.</p>", unsafe_allow_html=True)
    elif type_ == "three_principles":
        st.markdown("""
        <p>The three principles of conservation agriculture are:</p>
        <ul>
            <li>Minimal soil disturbance</li>
            <li>Permanent soil cover</li>
            <li>Diversity in crop rotations</li>
        </ul>""", unsafe_allow_html=True)
    elif type_ == "SBS_guide":
        st.markdown("""
        <p>Step by Step guide to implementing Good Agricultural Practices:</p>
        <ol>
            <li>Assess your current practices</li>
            <li>Plan improvements</li>
            <li>Implement changes gradually</li>
            <li>Monitor and adjust as needed</li>
        </ol>""", unsafe_allow_html=True)
    if st.button("Back to GAP menu"):
        update_step(GAP_1)
        st.experimental_rerun()

def Notifications_1():
    weather_active = st.session_state.notifications_enabled['weather']
    label = "Deactivate Weather Alerts" if weather_active else "Activate Weather Alerts"
    question = "What type of notifications would you like to receive?"
    options = [
        (label, Activate_weather_alerts),
        ("Crop Cultivation", lambda: Notifications_2('crop_cultivation')),
        ("Price Updates", lambda: Notifications_2('price_updates')),
        ("To begin", reset_to_start)
    ]
    render_with_back(question, options, show_back=False)

def Notifications_2(type_):
    if type_ == "weather_alerts":
        st.session_state.notifications_enabled['weather'] = True
        message = "<p>You will receive weather alerts for severe conditions.</p>"
        st.markdown(message, unsafe_allow_html=True)
        if st.button("Back to notifications"):
            update_step(Notifications_1)
            st.experimental_rerun()
    elif type_ == "crop_cultivation":
        question = "Toggle notifications for crops"
        options = [
            ("For crop 1", lambda: Activate_crop_alerts('crop_1')),
            ("For crop 2", lambda: Activate_crop_alerts('crop_2'))
        ]
        render_with_back(question, options)
    elif type_ == "price_updates":
        question = "What crop price updates would you like to receive?"
        options = [
            ("About crop 1", lambda: Activate_price_alerts('crop_1')),
            ("About crop 2", lambda: Activate_price_alerts('crop_2'))
        ]
        render_with_back(question, options)

def Activate_weather_alerts():
    st.session_state.notifications_enabled['weather'] = not st.session_state.notifications_enabled['weather']
    active = st.session_state.notifications_enabled['weather']
    message = ("<p> Weather alerts activated. You will now receive notifications for severe weather conditions.</p>"
               if active else
               "<p> Weather alerts deactivated. You will no longer receive weather notifications.</p>")
    st.markdown(message, unsafe_allow_html=True)
    label = "Deactivate Weather Alerts" if active else "Activate Weather Alerts"
    if st.button(label):
        Activate_weather_alerts()
        st.experimental_rerun()
    if st.button("Back to notifications"):
        update_step(Notifications_1)
        st.experimental_rerun()
    if st.button("To begin"):
        reset_to_start()
        st.experimental_rerun()

def Activate_crop_alerts(crop):
    st.markdown(f"<p>Notifications toggled for {crop}</p>", unsafe_allow_html=True)
    if st.button("Back to crop notifications"):
        update_step(lambda: Notifications_2('crop_cultivation'))
        st.experimental_rerun()

def Activate_price_alerts(crop):
    st.markdown(f"<p>Price update notifications toggled for {crop}</p>", unsafe_allow_html=True)
    if st.button("Back to price notifications"):
        update_step(lambda: Notifications_2('price_updates'))
        st.experimental_rerun()

def reset_to_start():
    st.session_state.history_stack = []
    st.session_state.branch_locked = False
    st.session_state.notifications_enabled = {'weather': False, 'crop': False}
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"
    update_step(render_welcome)

# On first load, start at welcome screen
if not st.session_state.history_stack:
    update_step(render_welcome)
else:
    st.session_state.history_stack[-1]()
