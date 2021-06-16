from data_grab import CA_grab, US_grab
from data_insert import setup_db, CA_insert_db, US_insert_db
from api.config import FRED_API_KEY, DB_URI
from api.config import FRED_URL, BOC_URL, BOC_SERIES, FRED_SERIES

def main() -> None:
    """The main script that runs the initial data download insert."""
    meta, engine = setup_db(DB_URI)
    conn = engine.connect()
    meta.reflect(engine)

    CA_grab(BOC_URL, BOC_SERIES)
    US_grab(FRED_URL, FRED_SERIES, FRED_API_KEY)
    
    try:
        CA_insert_db(conn, meta, BOC_SERIES)
        US_insert_db(conn, meta, FRED_SERIES)
        print("Data successfully inserted.")
    except Exception as err:
        print("Data already in database.")
        print(err)

    # Weekly update
    # automate(conn, meta, BOC_URL, BOC_SERIES, FRED_API_KEY, FRED_URL, FRED_SERIES)

if __name__ == '__main__':
    main()
