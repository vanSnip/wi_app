import streamlit as st

# Crop prices dictionary (put this near the top before session_state init)
crop_prices = {
    "crop_1": 215.25,
    "crop_2": 187.5,
}

# Initialize all session_state keys upfront to avoid AttributeErrors
if "notifications_weather" not in st.session_state:
    st.session_state.notifications_weather = False

# Use dict for crop notifications instead of individual keys
if "notifications_crop" not in st.session_state:
    st.session_state.notifications_crop = {crop: False for crop in crop_prices.keys()}

# Initialize the notification dictionary for price alerts if not exists
if "notifications_price" not in st.session_state:
    st.session_state.notifications_price = {crop: False for crop in crop_prices.keys()}

if "version" not in st.session_state:
    st.session_state.version = "data_saving"
if "version_show" not in st.session_state:
    st.session_state.version_show = "Data Saving Version"

if "branch_locked" not in st.session_state:
    st.session_state.branch_locked = False

if "history" not in st.session_state:
    st.session_state.history = []

def update_step(func):
    st.session_state.history.append(func)
    func()

def go_back():
    if len(st.session_state.history) > 1:
        st.session_state.history.pop()
        previous = st.session_state.history[-1]
        previous()

# Notifications menu main
def Notifications_1():
    st.session_state.branch_locked = True
    weather_label = "Deactivate Weather Alerts" if st.session_state.notifications_weather else "Activate Weather Alerts"
    st.markdown("What type of notifications would you like to receive?")
    if st.button(weather_label):
        update_step(activate_weather_alerts)
    if st.button("Crop Cultivation Notifications"):
        update_step(lambda: Notifications_2("crop_cultivation"))
    if st.button("Price Updates Notifications"):
        update_step(lambda: Notifications_2("price_updates"))
    if st.button("To begin"):
        st.experimental_rerun()

# Submenu for crop or price notifications
def Notifications_2(type_):
    st.session_state.branch_locked = True
    if type_ == "crop_cultivation":
        st.markdown("Toggle notifications for crop cultivation:")
        for crop in crop_prices.keys():
            status = "ON" if st.session_state.notifications_crop.get(crop, False) else "OFF"
            if st.button(f"{crop} cultivation notifications ({status})"):
                update_step(lambda c=crop: activate_crop_alerts(c))

    elif type_ == "price_updates":
        st.markdown("Toggle notifications for crop price updates:")
        for crop in crop_prices.keys():
            status = "ON" if st.session_state.notifications_price.get(crop, False) else "OFF"
            if st.button(f"{crop} price notifications ({status})"):
                update_step(lambda c=crop: activate_price_alerts(c))

    if st.button("Back to previous step"):
        go_back()

# Toggle weather alerts
def activate_weather_alerts():
    st.session_state.branch_locked = True
    st.session_state.notifications_weather = not st.session_state.notifications_weather
    status = "activated" if st.session_state.notifications_weather else "deactivated"
    st.markdown(f"Weather alerts {status}.")
    label = "Deactivate Weather Alerts" if st.session_state.notifications_weather else "Activate Weather Alerts"
    if st.button(label):
        update_step(activate_weather_alerts)
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

# Toggle crop cultivation notifications
def activate_crop_alerts(crop):
    st.session_state.branch_locked = True
    current_state = st.session_state.notifications_crop.get(crop, False)
    st.session_state.notifications_crop[crop] = not current_state
    status = "activated" if st.session_state.notifications_crop[crop] else "deactivated"
    st.markdown(f"Cultivation notifications for {crop} {status}.")
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

# Toggle crop price notifications
def activate_price_alerts(crop):
    st.session_state.branch_locked = True
    current_state = st.session_state.notifications_price.get(crop, False)
    st.session_state.notifications_price[crop] = not current_state
    status = "activated" if st.session_state.notifications_price[crop] else "deactivated"
    st.markdown(f"Price notifications for {crop} {status}.")
    if st.button("Back to notifications"):
        update_step(Notifications_1)
    if st.button("To begin"):
        st.experimental_rerun()

# Entry point (your main navigation loop)
if __name__ == "__main__":
    if "history" not in st.session_state or len(st.session_state.history) == 0:
        update_step(render_welcome)
    else:
        last_step = st.session_state.history[-1]
        last_step()
