import streamlit as st

# --- Style CSS ---
style = """
<style>
  body {
    font-family: Arial, sans-serif;
    background-color: #f9f9f9;
    color: #333;
    padding: 2em;
  }
  h2 {
    font-size: 1.5em;
  }
  .options {
    display: flex;
    margin-top: 1em;
    flex-direction: column;
    gap: 0.5em;
  }
  button {
    margin: 0.5em;
    padding: 0.5em 1.2em;
    font-size: 1em;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
  }
  button:hover {
    background-color: #0056b3;
  }
  .back-button {
    margin-top: 1em;
    background-color: #6c757d;
  }
  .back-button:hover {
    background-color: #5a6268;
  }
  .btn-container > button {
    display: block;
    width: fit-content;
    margin-bottom: 0.5em;
  }
</style>
"""

# Add CSS to Streamlit
st.markdown(style, unsafe_allow_html=True)

# --- Session state initialization ---
if "page_stack" not in st.session_state:
    st.session_state.page_stack = []

if "branch_locked" not in st.session_state:
    st.session_state.branch_locked = False

if "notifications_enabled" not in st.session_state:
    st.session_state.notifications_enabled = {"weather": False, "crop": False}

if "version" not in st.session_state:
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"

cropPrices = {
    "crop_1": 215.25,
    "crop_2": 187.5,
}

# --- Navigation helpers ---
def push_page(page_func):
    st.session_state.page_stack.append(page_func)

def go_back():
    if len(st.session_state.page_stack) > 1:
        st.session_state.page_stack.pop()

def render_page():
    st.write("")  # Spacer
    st.session_state.page_stack[-1]()

def button(text, on_click, key=None, css_class=""):
    # A helper to show buttons styled via CSS in markdown with Streamlit buttons
    # We'll just use Streamlit buttons as is; CSS applies globally
    return st.button(text, key=key, on_click=on_click)

# --- Render with question and options container ---
def render_with_back(question_text, options_funcs, show_back=True):
    st.markdown(f"<h2>{question_text}</h2>", unsafe_allow_html=True)
    # Use container with buttons
    for label, func in options_funcs:
        if func is not None:
            st.button(label, on_click=func, key=label)
        else:
            # If no func provided, disabled button or text
            st.markdown(f"<button disabled style='cursor:not-allowed;'>{label}</button>", unsafe_allow_html=True)
    if show_back and len(st.session_state.page_stack) > 1:
        st.button("⬅️ Back to previous step", on_click=go_back, key="back_button")

# --- Screens ---
def render_welcome():
    st.session_state.branch_locked = False
    opts = [
        ("Weather information", lambda: push_page(weather_info_1)),
        ("Crop Advice", lambda: push_page(crop_advice_1)),
        ("Price information for crops", lambda: push_page(price_info_1)),
        ("Good Agricultural Practices", lambda: push_page(GAP_1)),
        ("Notifications", lambda: push_page(notifications_1)),
        ("Version", lambda: push_page(version_1)),
    ]
    render_with_back("Welcome, what would you like to know?", opts, show_back=False)

# --- Version screens ---
def version_1():
    st.session_state.branch_locked = True
    opts = [
        ("Data Saving", lambda: push_page(data_saving_version)),
        ("Performance Optimised", lambda: push_page(performance_optimized_version)),
        ("Version for Extension Officers", lambda: push_page(extension_officer_version)),
        ("Go back to main menu", lambda: push_page(render_welcome)),
    ]
    render_with_back(
        f"Select the version you want, the current version is the {st.session_state.version_show}",
        opts,
        show_back=False,
    )

def extension_officer_version():
    st.session_state.version = "extension"
    st.session_state.version_show = "Extension Officers Version"
    opts = [("Go back to main menu", lambda: push_page(render_welcome))]
    render_with_back(
        "Extension Officers Version\n\nThis version includes tools and insights for agricultural extension services.",
        opts,
        show_back=False,
    )

def data_saving_version():
    st.session_state.version = "data_saving"
    st.session_state.version_show = "Data Saving Version"
    opts = [("Go back to main menu", lambda: push_page(render_welcome))]
    render_with_back(
        "Data Saving Version\n\nThis version is optimized for low data usage.",
        opts,
        show_back=False,
    )

def performance_optimized_version():
    st.session_state.version = "performance"
    st.session_state.version_show = "Performance Optimised Version"
    opts = [("Go back to main menu", lambda: push_page(render_welcome))]
    render_with_back(
        "Performance Optimised Version\n\nThis version prioritizes speed and performance for low-end devices.",
        opts,
        show_back=False,
    )

# --- Weather info ---
def weather_info_1():
    st.session_state.branch_locked = True
    version = st.session_state.version
    if version == "performance":
        image_md = "![Performance Graph](https://example.com/performance-graph.png)"
    elif version == "extension":
        image_md = "![Extension Graph](https://example.com/extension-graph.png)"
    else:
        image_md = "_Weather graphics are not available in this version to save data._"

    opts = [
        ("Go to forecasts", lambda: push_page(weather_forecasts_1)),
        ("Get weather advice for crops", lambda: push_page(weather_crop_advice_1)),
    ]
    st.markdown(f"### Weather Information\nThis is the current weather in the Mekong Delta.\n\n{image_md}")
    for label, func in opts:
        st.button(label, on_click=func, key=label)
    if len(st.session_state.page_stack) > 1:
        st.button("⬅️ Back to previous step", on_click=go_back, key="back_button")

def weather_crop_advice_1():
    st.session_state.branch_locked = True
    opts = [
        ("crop 1", lambda: push_page(lambda: weather_crop_advice_3("crop_1"))),
        ("crop 2", lambda: push_page(lambda: weather_crop_advice_3("crop_2"))),
    ]
    render_with_back("For what crop do you need weather advice?", opts)

def weather_crop_advice_3(crop):
    st.session_state.branch_locked = True
    st.markdown(f"### Weather advice for {crop}\n\n*Details for {crop} weather advice here...*")
    st.button("Back to previous step", on_click=go_back, key="back_button")

def weather_forecasts_1():
    st.session_state.branch_locked = True
    opts = [
        ("Get forecast for period 1", lambda: push_page(lambda: weather_forecasts_2("period_1"))),
        ("Get forecast for period 2", lambda: push_page(lambda: weather_forecasts_2("period_2"))),
    ]
    render_with_back("This is the weather forecast {Insert uploaded graph}", opts)

def weather_forecasts_2(period):
    st.session_state.branch_locked = True
    if period == "period_1":
        message = """
        This is the forecast for period 1.
        ![Example image](https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png)
        """
    else:
        message = """
        This is the forecast for period 2.
        ![Example image](https://www.nahss.nl/wp-content/uploads/2023/05/NAHSS-logo-text-without-background-600x236.png)
        """
    st.markdown(message)
    st.button("Back to previous step", on_click=go_back, key="back_button")

# --- Crop advice ---
def crop_advice_1():
    st.session_state.branch_locked = True
    opts = [
        ("Cultivation", lambda: push_page(lambda: crop_advice_2("cultivation"))),
        ("Pest and diseases", lambda: push_page(lambda: crop_advice_2("pest_and_diseases"))),
    ]
    render_with_back("For what crop do you need advice?", opts)

def crop_advice_2(type_):
    st.session_state.branch_locked = True
    if type_ == "pest_and_diseases":
        message = "What type of crop do you need advice for pest and disease management?"
        opts = [
            ("crop_1", lambda: push_page(lambda: pnd_1("crop_1"))),
            ("crop_2", lambda: push_page(lambda: pnd_1("crop_2"))),
        ]
    else:
        message = "For what crop do you need advice?"
        opts = [
            ("crop_1", lambda: push_page(lambda: crop_cultivation_adv("crop_1"))),
            ("crop_2", lambda: push_page(lambda: crop_cultivation_adv("crop_2"))),
        ]
    render_with_back(message, opts)

def pnd_1(crop):
    st.markdown(f"### Pest and Disease advice for {crop}\n\n*Details here...*")
    st.button("Back to previous step", on_click=go_back, key="back_button")

def crop_cultivation_adv(crop):
    st.markdown(f"### Cultivation advice for {crop}\n\n*Details here...*")
    st.button("Back to previous step", on_click=go_back, key="back_button")

# --- Price info ---
def price_info_1():
    st.session_state.branch_locked = True
    opts = [
        (f"crop_1 - ${cropPrices['crop_1']:.2f}", lambda: push_page(lambda: price_info_2("crop_1"))),
        (f"crop_2 - ${cropPrices['crop_2']:.2f}", lambda: push_page(lambda: price_info_2("crop_2"))),
    ]
    render_with_back("What crop do you want to know the historical prices of?", opts)

def price_info_2(crop):
    st.markdown(f"### Historical price data for {crop}\n\n{{Insert table}} and it is sold at {{insert location}}")
    st.button("Back to previous step", on_click=go_back, key="back_button")

# --- Good Agricultural Practices ---
def GAP_1():
    st.session_state.branch_locked = True
    opts = [
        ("Conservation Agriculture", lambda: push_page(lambda: GAP_2("Conservation_agriculture"))),
        ("3 principles of conservation agriculture", lambda: push_page(lambda: GAP_2("three_principles"))),
        ("Step by Step guide", lambda: push_page(lambda: GAP_2("SBS_guide"))),
    ]
    render_with_back("What type of Good Agricultural Practices do you want to know about?", opts)

def GAP_2(type_):
    st.session_state.branch_locked = True
    if type_ == "Conservation_agriculture":
        message = """
        Conservation Agriculture is a sustainable farming practice that improves soil health and productivity.
        """
    elif type_ == "three_principles":
        message = """
        The three principles of conservation agriculture are:
        - Minimal soil disturbance
        - Permanent soil cover
        - Diversity in crop rotations
        """
    elif type_ == "SBS_guide":
        message = """
        Step by Step guide to implementing Good Agricultural Practices:
        1. Assess your current practices
        2. Plan improvements
        3. Implement changes gradually
        4. Monitor and adjust as needed
        """
    else:
        message = "Unknown category"
    st.markdown(message)
    st.button("Back to previous step", on_click=go_back, key="back_button")

# --- Notifications ---
def notifications_1():
    st.session_state.branch_locked = True
    weather_status = st.session_state.notifications_enabled.get("weather", False)
    weather_label = "Deactivate Weather Alerts" if weather_status else "Activate Weather Alerts"
    opts = [
        (weather_label, lambda: push_page(activate_weather_alerts)),
        ("Crop Cultivation", lambda: push_page(lambda: notifications_2("crop_cultivation"))),
        ("Price Updates", lambda: push_page(lambda: notifications_2("price_updates"))),
    ]
    render_with_back("What type of notifications would you like to receive?", opts, show_back=False)
    if len(st.session_state.page_stack) > 1:
        st.button("⬅️ Back to previous step", on_click=go_back, key="back_button")

def notifications_2(type_):
    st.session_state.branch_locked = True
    if type_ == "weather_alerts":
        st.session_state.notifications_enabled["weather"] = True
        message = f"""
        You will receive weather alerts for severe conditions.<br>
        Weather alerts: {"Active" if st
