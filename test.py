import streamlit as st
import streamlit.components.v1 as components

# Your full HTML content as a string (paste your whole HTML here)
with open("test.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# Render your HTML + JS in Streamlit using components.html
components.html(html_code, height=700, scrolling=True)
