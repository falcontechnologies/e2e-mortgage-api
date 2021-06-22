#!/usr/local/bin/python3.9
from data_grab import CA_grab
from data_insert import CA_insert_db, setup_db
from api.config import DB_URI
from api.config import BOC_URL, BOC_SERIES
meta, engine = setup_db(DB_URI)
conn = engine.connect()
meta.reflect(engine)

# Grab and insert the latest BoC series data
CA_grab(BOC_URL, BOC_SERIES, True)
CA_insert_db(conn, meta, BOC_SERIES)
print("CA weekly data was successfully inserted")




