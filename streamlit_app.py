import streamlit as st



st.title("Streamlit Cat API")
st.write(
    "A simple Streamlit app that uses the Cat API to generate random cats and display them in the app."
)

pages = [
    st.Page("Gallery", "pages/gallery.py"),
    st.Page("Favorites", "pages/favorites.py"),
    st.Page("Settings", "pages/settings.py"),
]
current_page = st.navigation(pages)
current_page.run()
