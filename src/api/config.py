import os
from dotenv import load_dotenv

load_dotenv()
FRED_API_KEY = os.environ['FRED_API_KEY']

user = os.environ["POSTGRES_USER"]
password = os.environ["POSTGRES_PASSWORD"]
host = os.environ["POSTGRES_HOST"]
port = os.environ["POSTGRES_PORT"]
database = os.environ["POSTGRES_DATABASE"]

DB_URI = f"postgresql://{user}:{password}@{host}:{port}/{database}"

# Base URLs for banking websites' API
BOC_URL = "https://www.bankofcanada.ca/valet/observations"
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"

# Bank series that will be stored in database
BOC_SERIES = ['V80691311', 'V80691333', 'V80691334', 'V80691335']
FRED_SERIES = ['PRIME', 'MORTGAGE5US', 'MORTGAGE15US', 'MORTGAGE30US']
