import json
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, Float
from collections import defaultdict

from datetime import datetime

# Type hinting documentation
from typing import Tuple, List
from sqlalchemy.engine.base import Engine, Connection

def setup_db(db_uri: str) -> Tuple[MetaData, Engine]:
    """Create the BoC rates and FRED rates tables in the database."""
    meta = MetaData()
    boc_rates = Table(
        'boc_rates', meta, 
        Column('date', String, primary_key=True), 
        Column('prime_rate', Float(2)), 
        Column('one_year_conventional_mortgage', Float(2)),
        Column('three_year_conventional_mortgage', Float(2)),
        Column('five_year_conventional_mortgage', Float(2)),
    )
    fred_rates = Table(
        'fred_rates', meta, 
        Column('date', String, primary_key=True), 
        Column('prime_rate', Float(2)), 
        Column('five_year_average_mortgage', Float(2)),
        Column('fifteen_year_average_mortgage', Float(2)),
        Column('thirty_year_average_mortgage', Float(2)),
    )
    users = Table(
        'users', meta,
        Column('account_id', String, primary_key=True),
        Column('name', String),
        Column('email', String),
        Column('api_key', String),
        Column('session_key', String, nullable=True), # Generated when using API
                                                      # Expires after set time
        Column('registered', String),
        Column('updated', String, nullable=True) # May have no updates
    )
    engine = create_engine(db_uri)
    meta.create_all(engine, checkfirst=True)
    return meta, engine

def CA_insert_db(
    conn: Connection, meta: MetaData, boc_series: List[str]
    ) -> None:
    """Insert the BoC data into the database."""
    # Bank of Canada table insertion
    boc_rates = meta.tables['boc_rates']

    with open("data/BoC-Data.JSON", "r") as jsonfile:
        data = json.load(jsonfile)

    for entry in data['observations']:
        # Iterate through each rate and add None for missing values
        rates = {}
        for rate in boc_series:
            rates[rate] = entry[rate]['v'] if rate in entry else None
        if all(value is None for value in rates.values()):
            continue
        
        ex = boc_rates.insert().values(
            date=entry['d'],
            prime_rate=rates['V80691311'],
            one_year_conventional_mortgage=rates['V80691333'],
            three_year_conventional_mortgage=rates['V80691334'],
            five_year_conventional_mortgage=rates['V80691335']
        )
        result = conn.execute(ex)

def US_insert_db(
    conn: Connection, meta: MetaData, fred_series: List[str]
    ) -> None:
    """Insert the FRED data into the database."""
    # Federal Reserve Economic Data table insertion
    fred_rates = meta.tables['fred_rates']
    
    # Create a single dictionary with values of all four series
    combined_data = defaultdict(dict)
    for series in fred_series:
        with open(f"data/FRED-{series}-Data.json", "r") as jsonfile:
            data = json.load(jsonfile)

            for entry in data['observations']:
                # Empty values are listed as single dot
                if entry['value'] == '.':
                    continue
                combined_data[entry['date']][series] = entry['value']

    for date, rates in combined_data.items():
        # Some dates only have observations for certain series
        # Check for missing series and add with value of None
        for series in fred_series:
            if not series in rates:
                rates[series] = None

        ex = fred_rates.insert().values(
            date=date,
            prime_rate=rates['PRIME'],
            five_year_average_mortgage=rates['MORTGAGE5US'],
            fifteen_year_average_mortgage=rates['MORTGAGE15US'],
            thirty_year_average_mortgage=rates['MORTGAGE30US']
        )
        result = conn.execute(ex)

def new_user(
    conn: Connection, meta: MetaData, name, email
    ) -> None:
    users = meta.tables['users']

    ex = users.insert().values(
        account_id="",
        name=name,
        email=email,
        api_key="",
        registered=datetime.now(),
        updated=None)

    result = conn.execute(ex)
