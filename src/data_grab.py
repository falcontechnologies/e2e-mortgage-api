import requests

# Type hinting documentation
from typing import List

def CA_grab(boc_url: str, boc_series: List[str],
            weekly: bool=False) -> None:
    """Make a http request to the BoC site for series data."""
    with open(f"data/BoC-Data.json", "wb") as jsonfile:
        boc_request_url = boc_url + f"/{','.join(boc_series)}/json?"
        if weekly:
            boc_request_url += "recent=1"
        jsonfile.write(requests.get(boc_request_url).content)

def US_grab(fred_url: str, fred_series: List[str], fred_api_key: str,
            weekly: bool=False) -> None:
    """Make a http request to the FRED site for series data."""
    for series in fred_series:
        with open(f"data/FRED-{series}-Data.json", "wb") as jsonfile:
            fred_request_url = (fred_url + f"?series_id={series}" +
                                f"&api_key={fred_api_key}&file_type=json")
            if weekly:
                fred_request_url += "&limit=1&sort=desc"
            jsonfile.write(requests.get(fred_request_url).content)
