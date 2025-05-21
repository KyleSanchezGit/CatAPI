import streamlit as st
import requests
import time
import hashlib
import logging
from datetime import datetime
from typing import List, Optional
import validators
from typing import Dict, Any
from PIL import Image
from io    import BytesIO


# ─── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🐱 Cat Image Generator",
    page_icon="😺",
    layout="wide",
)

API_BASE_URL = "https://cataas.com"
RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 3
DEFAULT_IMAGE_SIZE = (400, 400)

# ─── SESSION-STATE SETUP ────────────────────────────────────────────────────────
if 'last_api_call'   not in st.session_state: st.session_state.last_api_call = 0
if 'favorites'       not in st.session_state: st.session_state.favorites   = {}
if 'api_call_count'  not in st.session_state: st.session_state.api_call_count = 0
if 'gen'             not in st.session_state: st.session_state.gen = 0

def rate_limit_check() -> bool:
    now = time.time()
    if now - st.session_state.last_api_call < RATE_LIMIT_SECONDS:
        return False
    st.session_state.last_api_call = now
    st.session_state.api_call_count += 1
    return True

@st.cache_data(ttl=3600)
def fetch_tags() -> List[str]:
    if not rate_limit_check():
        return []
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(f"{API_BASE_URL}/api/tags", timeout=5)
            resp.raise_for_status()
            tags = resp.json()
            if not isinstance(tags, list):
                raise ValueError("Malformed tags list")
            return sorted(tags)
        except Exception as e:
            logging.warning(f"fetch_tags attempt {attempt+1} failed: {e}")
            time.sleep(2 ** attempt)
    st.error("Could not load cat tags. Try again later.")
    return []

def validate_url(url: str) -> bool:
    return bool(validators.url(url) and url.startswith(API_BASE_URL))


def get_cat_url(tag: str) -> Optional[str]:
    """Fetch a random cat (optionally by tag) via the JSON API."""
    if not rate_limit_check():
        st.warning("Rate limit: slow down a bit 😉")
        return None

    endpoint = "/cat" + (f"/{tag}" if tag else "")
    try:
        resp = requests.get(
            f"{API_BASE_URL}{endpoint}?json=true",
            timeout=5,
            headers={"User-Agent": "Streamlit-Cat-App"},
        )
        resp.raise_for_status()
        data = resp.json()
        return f"{API_BASE_URL}{data['url']}"
    except Exception as e:
        logging.warning(f"get_cat_url failed: {e}")
        st.error("Failed to get cat image. Try again later.")
        return None



def save_favorite(url: str, tag: str):
    if not validate_url(url):
        st.error("Invalid URL")
        return

    # Limit total favorites
    if len(st.session_state.favorites) >= 50:
        st.warning("Maximum favorites limit reached. Remove some old favorites first.")
        return

    key = hashlib.sha256(url.encode()).hexdigest()
    st.session_state.favorites[key] = {
        "url": url,
        "tag": tag,
        "added": datetime.now().isoformat(),
    }
    st.success("❤️ Added to favorites!")


def show_favorites():
    favs = st.session_state.favorites
    if not favs:
        st.info("No favorites yet!")
        return
    st.subheader("Your Favorites")
    cols = st.columns(3)
    for i,(k,v) in enumerate(favs.items()):
        with cols[i % 3]:
            st.image(v["url"], caption=v["tag"])
            if st.button("Remove", key=f"rm_{k}"):
                st.session_state.favorites.pop(k)
                st.experimental_rerun()

def main():
    st.title("🐱 Cat Image Generator")
    st.write("Generate and save your favorite cat pics from cataas.com!")

    # ── Sidebar UI ────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Settings")
        w = st.slider("Width",  100, 800, DEFAULT_IMAGE_SIZE[0], 50)
        h = st.slider("Height", 100, 800, DEFAULT_IMAGE_SIZE[1], 50)
        show_fav = st.checkbox("Show Favorites")
        st.markdown("---")
        st.header("API Usage")
        st.write(f"Calls today: {st.session_state.api_call_count}")

    # ── Fetch tags & build controls ──────────────────────────────────────────────
    tags = fetch_tags()
    choice = None
    if tags:
        c1,c2 = st.columns([3,1])
        with c1:
            choice = st.selectbox("Pick a tag (or leave blank):", [""] + tags)
        with c2:
            if st.button("🎲 Generate"):
                st.session_state.gen += 1

    # ── Show image & favorite button ─────────────────────────────────────────────
    if st.session_state.gen > 0:
        url = get_cat_url(choice)
        if url:
            try:
                resp = requests.get(url, timeout=5)
                resp.raise_for_status()
                img = Image.open(BytesIO(resp.content))
                st.image(img,
                         caption=f"{choice or 'Random'} cat",
                         use_container_width=True)
            except Exception as e:
                st.error("Failed to download/display image")

            if st.button("❤️ Favorite this"):
                save_favorite(url, choice)

    # ── Favorites section ─────────────────────────────────────────────────────────
    if show_fav:
        st.markdown("---")
        show_favorites()

if __name__ == "__main__":
    main()
