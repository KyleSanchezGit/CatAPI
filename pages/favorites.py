# pages/favorites.py
import streamlit as st
import requests
from PIL       import Image
from io        import BytesIO

st.set_page_config(page_title="🐾 Favorites")
st.title("🐾 Your Favorite Cats")

favs = st.session_state.get("favorites", {})
if not favs:
    st.info("No favorites saved yet.")
else:
    cols = st.columns(3)
    for i, (key, fav) in enumerate(favs.items()):
        with cols[i % 3]:
            try:
                resp = requests.get(fav["url"], timeout=5)
                resp.raise_for_status()
                img = Image.open(BytesIO(resp.content))
                st.image(img, caption=fav["tag"], use_container_width=True)
            except Exception:
                st.error("Couldn’t load that favorite.")

            if st.button("Remove", key=f"rm_{key}"):
                st.session_state.favorites.pop(key)
                st.experimental_rerun()
