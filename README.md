## Overview

CatAPI is a Streamlit-based web application that fetches and displays random cat images from the Cataas REST API, providing a playful and interactive way to enjoy feline photos right in your browser ([Cataas][1], [Streamlit Docs][2]). It leverages Python’s Requests library for HTTP calls, implements rate limiting and retry logic for robust API interaction, and uses Streamlit’s session state to let you save and revisit your favorite cats ([Requests][3], [Streamlit Docs][2]).

## Features

* **Random Cat Images**: Retrieve a random cat image on each click using the Cataas `/cat` endpoint and Python’s `requests.get` method ([PublicAPI][4], [Requests][3]).
* **Image Customization**: Overlay custom text on cats via the Cataas `/cat/says/{text}` endpoint for personalized captions ([Cataas][1]).
* **Rate Limiting & Retries**: Enforce a 2-second pause between API calls and retry up to 3 times on failures using Python’s `time.sleep` and loop logic ([Requests][3]).
* **Favorites Management**: Save and view your favorite cat images across the session with Streamlit’s `st.session_state` mechanism ([Streamlit Docs][2]).
* **URL Validation**: Ensure that any custom image URLs or tags are valid with the `validators` library before making API calls ([PyPI][5]).
* **Responsive UI**: Wide-layout and custom page title/icon configuration via `st.set_page_config` for an optimal viewing experience ([Streamlit Docs][2]).

## Demo

Try it live on Streamlit Cloud:
[https://catimagesapi.streamlit.app/](https://catimagesapi.streamlit.app/)

## Installation

Clone the repository and install dependencies with pip:

```bash
git clone https://github.com/KyleSanchezGit/CatAPI.git  
cd CatAPI  
pip install -r requirements.txt  
```

([pip][6])

## Usage

Run the app locally with Streamlit:

```bash
streamlit run streamlit_app.py
```

Then open the provided `localhost` URL in your browser. ([Streamlit Docs][2])

## License

This project is licensed under the Apache-2.0 License. ([GitHub][7])

## Contact

For questions or feedback, open an issue on the [GitHub repository](https://github.com/KyleSanchezGit/CatAPI) or reach out to Kyle Sanchez via GitHub.

[1]: https://cataas.com/ "Cat as a service (CATAAS)"
[2]: https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config "st.set_page_config - Streamlit Docs"
[3]: https://requests.readthedocs.io/ "Requests: HTTP for Humans™ — Requests 2.32.3 documentation"
[4]: https://publicapi.dev/cataas-api "Cataas API - PublicAPI"
[5]: https://pypi.org/project/validators/ "validators - PyPI"
[6]: https://pip.pypa.io/en/stable/getting-started/ "Getting Started - pip documentation v25.1.1"
[7]: https://github.com/KyleSanchezGit/CatAPI "GitHub - KyleSanchezGit/CatAPI"
