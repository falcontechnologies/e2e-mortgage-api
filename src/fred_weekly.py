from data_grab import US_grab
from data_insert import US_insert_db, setup_db
from api.config import DB_URI, FRED_API_KEY
from api.config import FRED_URL, FRED_SERIES

meta, engine = setup_db(DB_URI)
conn = engine.connect()
meta.reflect(engine)

# Grab and insert the latest FRED series data
US_grab(FRED_URL, FRED_SERIES, FRED_API_KEY, True)
US_insert_db(conn, meta, FRED_SERIES)
