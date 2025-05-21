import streamlit as st
import requests
from typing import List, Optional, Dict
import time
from datetime import datetime
import json
import hashlib

# Constants
API_BASE_URL = "https://cataas.com"
RATE_LIMIT_SECONDS = 2
MAX_RETRIES = 3
DEFAULT_IMAGE_SIZE = (400, 400)

# Initialize session state for rate limiting and favorites
if 'last_api_call' not in st.session_state:
    st.session_state.last_api_call = 0
if 'favorites' not in st.session_state:
    st.session_state.favorites = {}
if 'api_call_count' not in st.session_state:
    st.session_state.api_call_count = 0


def rate_limit_check() -> bool:
    """Check if we should rate limit the API calls."""
    current_time = time.time()
    if current_time - st.session_state.last_api_call < RATE_LIMIT_SECONDS:
        return False
    st.session_state.last_api_call = current_time
    return True


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_tags() -> List[str]:
    """Fetch available cat tags from the API with retry logic."""
    if not rate_limit_check():
        st.warning("Please wait a moment before requesting more data.")
        return []

    for attempt in range(MAX_RETRIES):
        try:
            with st.spinner("Fetching available tags..."):
                response = requests.get(
                    f"{API_BASE_URL}/api/tags",
                    timeout=5,
                    headers={"User-Agent": "Streamlit-Cat-App"}
                )
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, list):
                    raise ValueError("Expected a list of tags from API")
                return sorted(data)  # Sort tags alphabetically
        except requests.RequestException as e:
            logging.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                st.error(f"Error fetching tags: {str(e)}")
                return []
        except ValueError as e:
            logging.error(f"Invalid data received from API: {str(e)}")
            st.error("Error processing API response")
            return []
        time.sleep(min(2 ** attempt, 8))  # Exponential backoff with max delay


def get_cat_image(tag: str, size: tuple = DEFAULT_IMAGE_SIZE) -> Optional[str]:
    """Fetch cat image URL with size parameters and validation."""
    if not rate_limit_check():
        st.warning("Please wait a moment before requesting more images.")
        return None

    # Sanitize tag input
    tag = tag.strip().lower()
    if not tag.isalnum() and not all(c in '-_' for c in tag if not c.isalnum()):
        st.error("Invalid tag format")
        return None

    try:
        # Add size parameters to URL
        width, height = size
        url = f"{API_BASE_URL}/cat/{tag}?width={width}&height={height}"

        # Verify image URL is accessible
        response = requests.head(url, timeout=5)
        response.raise_for_status()
        return url
    except Exception as e:
        st.error(f"Error getting cat image: {str(e)}")
        return None


def save_to_favorites(image_url: str, tag: str):
    """Save image to favorites with timestamp."""
    image_hash = hashlib.md5(image_url.encode()).hexdigest()
    st.session_state.favorites[image_hash] = {
        'url': image_url,
        'tag': tag,
        'timestamp': datetime.now().isoformat(),
    }
    st.success("Added to favorites!")


def display_favorites():
    """Display all favorite images."""
    if not st.session_state.favorites:
        st.info("No favorites saved yet!")
        return

    st.subheader("Your Favorite Cats")
    cols = st.columns(3)
    for idx, (_, favorite) in enumerate(st.session_state.favorites.items()):
        with cols[idx % 3]:
            st.image(favorite['url'], caption=f"Tag: {favorite['tag']}")
            if st.button(f"Remove {favorite['tag']}", key=f"remove_{idx}"):
                st.session_state.favorites.pop(favorite['url'], None)
                st.rerun()


def main():
    st.title("🐱 Enhanced Cat Image Generator")
    st.write("Generate and collect your favorite cat images!")

    '''''# Settings sidebar
    with st.sidebar:
        st.subheader("Settings")
        image_width = st.slider("Image Width", 100, 800, DEFAULT_IMAGE_SIZE[0], 50)
        image_height = st.slider("Image Height", 100, 800, DEFAULT_IMAGE_SIZE[1], 50)
        show_favorites = st.checkbox("Show Favorites") '''

    # Main content
    tags = fetch_tags()

    if tags:
        col1, col2 = st.columns([3, 1])
        with col1:
            choice = st.selectbox("Select a cat breed/tag:", tags)
        with col2:
            if st.button("Generate New Cat", type="primary"):
                st.session_state.current_image = None  # Force new image

        if choice:
            with st.spinner("Loading cat image..."):
                image_url = get_cat_image(choice, (image_width, image_height))
                if image_url:
                    st.image(image_url, caption=f"A {choice} cat", use_column_width=True)

                    # Favorite button
                    if st.button("❤️ Add to Favorites"):
                        save_to_favorites(image_url, choice)
    else:
        st.warning("No tags available. Please try again later.")

    # Display favorites if enabled
    if show_favorites:
        st.markdown("---")
        display_favorites()

    # Display API usage statistics
    with st.sidebar:
        st.markdown("---")
        st.subheader("API Usage Stats")
        st.write(f"API calls today: {st.session_state.api_call_count}")


if __name__ == "__main__":
    main()

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
