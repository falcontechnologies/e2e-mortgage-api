import flask
from flask import request, abort, jsonify, render_template, redirect, url_for
from sqlalchemy import create_engine, MetaData
from sqlalchemy import select
from config import DB_URI
import logging

# Type hinting documentation
from typing import Tuple
from flask import Response
from sqlalchemy.engine.base import Engine

logging.basicConfig(
    filename='.log', format='%(asctime)s %(levelname)s:%(message)s'
)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)
app.config["DEBUG"] = True # TODO remove this before deployment

def setup_db(DB_URI: str) -> Tuple[Engine, MetaData]:
    """Create the database metadata and engine connection."""
    meta = MetaData()
    engine = create_engine(DB_URI)
    meta.reflect(engine)
    return meta, engine

@app.route('/', methods=['GET'])
def home() -> Response:
    """The home page for the API."""
    return redirect(url_for('docs'))

@app.route('/docs', methods=['GET'])
def docs() -> Response:
    """The documentation for the API."""
    return render_template('docs.html')

@app.route('/series/', methods=['GET'])
@app.route('/series/<bank_name>', methods=['GET'])
def series(bank_name: str=None) -> Response:
    """The main API page where http requests are made."""
    if not connected:
        logger.info("attempt to access data when not connected to database")
        abort(500)

    with engine.connect() as conn:
        if bank_name is None:
            return redirect(url_for('docs'))
            
        table = {}
        bank_table_name = f"{bank_name}_rates"

        if not bank_table_name in meta.tables:
            abort(400, description=f"Bank {bank_name} not found.")

        bank_rates = meta.tables[bank_table_name]
        keys = bank_rates.columns.keys()
        _, *series = keys

        if 'series' in request.args:
            series = request.args['series'].split(',')
            not_found = []
            for key in series:
                if not key in keys:
                    not_found.append(key)
            if len(not_found) > 0:
                not_found = ', '.join(not_found)
                abort(400, description=f"Series {not_found} not found.")
            keys = ['date'] + series

        ex = select(*[getattr(bank_rates.c, key) for key in keys])

        if 'start_date' in request.args:
            ex = ex.where(bank_rates.c.date >= request.args['start_date'])

        if 'end_date' in request.args:
            ex = ex.where(bank_rates.c.date <= request.args['end_date'])

        if 'hide_none' in request.args and request.args['hide_none'] == 'true':
            for key in series:
                ex = ex.where(getattr(bank_rates.c, key) != None)

        if 'offset' in request.args:
            offset = request.args['offset']
            if int(offset) < 0:
                abort(400, "offset must not be negative.")
            ex = ex.offset(offset)

        if 'limit' in request.args:
            limit = request.args['limit']
            if int(limit) < 0:
                abort(400, "limit must not be negative.")
            ex = ex.limit(limit)

        result = conn.execute(ex)
        for date, *values in result:
            row = {}
            for key, value in zip(series, values):
                row[key] = value
            table[date] = row

    return jsonify(table)

@app.errorhandler(400)
def api_request_error(err):
    """The handler for bad requests to the API."""
    return jsonify({'error': f"{err}"}), 400

# This won't run if imported by flask
#if __name__ == '__main__':
try:
    meta, engine = setup_db(DB_URI)
    connected = True
except Exception as err:
    logger.error("could not connect to %s", DB_URI)
    connected = False

app.run()
