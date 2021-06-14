import schedule
from data_grab import CA_grab, US_grab
from data_insert import CA_insert_db, US_insert_db

# Type hinting documentation
from typing import List
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Connection

def automate(
    conn: Connection, meta: MetaData, boc_url: str, boc_series: List[str],
    fred_api_key: str, fred_url: str, fred_series: List[str]
    ) -> None:
    """
    Schedule the BoC and FRED series data to be downloaeded
    on a weekly interval.
    """
    def CA_weekly_update() -> None:
        """Grab the latest BoC series data."""
        CA_grab(boc_url, boc_series, True)
        CA_insert_db(conn, meta, boc_series)

    def US_weekly_update() -> None:
        """Grab the latest FRED series data."""
        US_grab(fred_url, fred_series, fred_api_key, True)
        US_insert_db(conn, meta, fred_series)
        
    schedule.every().wednesday.at("23:00").do(CA_weekly_update)
    schedule.every().thursday.at("23:00").do(US_weekly_update)

    while True:
        schedule.run_pending()
