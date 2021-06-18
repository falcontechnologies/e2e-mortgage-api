from data_grab import CA_grab, US_grab
from data_insert import setup_db, CA_insert_db, US_insert_db
from api.config import FRED_API_KEY, DB_URI
from api.config import FRED_URL, BOC_URL, BOC_SERIES, FRED_SERIES

import logging
from psycopg2.errors import UniqueViolation

def main() -> None:
    """The main script that runs the initial data download insert."""
    logging.basicConfig(
        filename='.log', format='%(asctime)s %(levelname)s:%(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        CA_grab(BOC_URL, BOC_SERIES)
        logger.info("sucessfully grabbed %s data from %s",
                    ', '.join(BOC_SERIES), BOC_URL)
        US_grab(FRED_URL, FRED_SERIES, FRED_API_KEY)
        logger.info("sucessfully grabbed %s data from %s using API key %s",
                    ', '.join(BOC_SERIES), BOC_URL, FRED_API_KEY)
    except FileNotFoundError:
        logger.error("directory data does not exist")
        return
    except:
        logger.error("data could not be grabbed")
        return

    try:
        meta, engine = setup_db(DB_URI)
        logger.info("sucessfully connected to %s", DB_URI)
    except:
        logger.error("could not connect to %s", DB_URI)
        return

    conn = engine.connect()
    meta.reflect(engine)

    try:
        CA_insert_db(conn, meta, BOC_SERIES)
        US_insert_db(conn, meta, FRED_SERIES)
        logger.info("data successfully inserted into %s", DB_URI)
    except UniqueViolation:
        logger.error("data already in %s", DB_URI)
    except:
        logger.error("uncaught error")

if __name__ == '__main__':
    main()
