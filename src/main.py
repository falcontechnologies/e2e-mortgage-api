from data_grab import CA_grab, US_grab
from data_insert import setup_db, CA_insert_db, US_insert_db
from automate_weekly import automate
from api.config import FRED_API_KEY, DB_URI

# Bank series that will be stored in database
BOC_SERIES = ['V80691311', 'V80691333', 'V80691334', 'V80691335']
FRED_SERIES = ['PRIME', 'MORTGAGE5US', 'MORTGAGE15US', 'MORTGAGE30US']

# Base URLs for banking websites' API
BOC_URL = "https://www.bankofcanada.ca/valet/observations"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

def main() -> None:
    """
    The main script that runs the initial data download
    insert and scheduled weekly data downloads.
    """
    try:
        meta, engine = setup_db(DB_URI)
    except:
        print("Could not connect to database.")
        return
    conn = engine.connect()
    meta.reflect(engine)

    CA_grab(BOC_URL, BOC_SERIES)
    US_grab(FRED_URL, FRED_SERIES, FRED_API_KEY)
    
    try:
        CA_insert_db(conn, meta, BOC_SERIES)
        US_insert_db(conn, meta, FRED_SERIES)
        print("Data successfully inserted.")
    except: # Exception is psycopg2.errors.UniqueViolation
        print("Data already in database.")

    # Weekly update
    automate(conn, meta, BOC_URL, BOC_SERIES, FRED_API_KEY, FRED_URL, FRED_SERIES)

if __name__ == '__main__':
    main()
