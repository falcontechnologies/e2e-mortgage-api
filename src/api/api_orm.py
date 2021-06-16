from flask import Flask, request, jsonify, redirect, url_for, render_template, abort
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from config import DB_URI

#typing
from flask import Response

Base = declarative_base()

app = Flask(__name__, template_folder='template')
app.config["DEBUG"] = True

engine = create_engine(DB_URI)

Session = sessionmaker(engine)
session = Session()

class Boc_rates(Base):
    """Bank of Canada rates."""
    __tablename__ = 'boc_rates'

    date = Column(String, primary_key=True)
    prime_rate = Column(Float(2))
    one_year_conventional_mortgage = Column(Float(2))
    three_year_conventional_mortgage = Column(Float(2))
    five_year_conventional_mortgage = Column(Float(2))
    all_params = ['date', 'prime_rate', 'one_year_conventional_mortgage',
                        'three_year_conventional_mortgage', 'five_year_conventional_mortgage']

    def get_columns(self, params=None):
        """Returns values of all or specified table columns."""
        if params == None:
            return [self.date, self.prime_rate, self.one_year_conventional_mortgage, 
                        self.three_year_conventional_mortgage, self.five_year_conventional_mortgage]
        else:
            series = [self.date] + [getattr(self, param) for param in params]
            return series

    def get_keys(self, params=None):
        """Returns all or specified table keys."""
        
        return [attr for attr in dir(self) if (attr in params)]

class Fred_rates(Base):
    """Federal Reserve rates."""
    __tablename__ = 'fred_rates'

    date = Column(String, primary_key=True)
    prime_rate = Column(Float(2))
    five_year_average_mortgage = Column(Float(2))
    fifteen_year_average_mortgage = Column(Float(2))
    thirty_year_average_mortgage = Column(Float(2))
    all_params = ['date', 'prime_rate', 'five_year_average_mortgage',
                            'fifteen_year_average_mortgage', 'thirty_year_average_mortgage']

    def get_columns(self, params):
        """Returns values of all or specified table columns."""
        
        series = [self.date] + [getattr(self, param) for param in params]
        return series

    def get_keys(self, params=None):
        """Returns all or specified table keys."""
       
        return [attr for attr in dir(self) if (attr in params)]

Base.metadata.create_all(engine)

@app.route('/', methods=['GET'])
def home() -> Response:
    return redirect(url_for('docs'))

@app.route('/docs', methods=['GET'])
def docs() -> Response:
    """The documentation for the API."""
    return render_template('docs.html')

@app.route('/series', methods=['GET'])
@app.route('/series/<bank_name>', methods=['GET'])
def series(bank_name: str=None) -> Response:
    """Default bank -> boc"""

    if bank_name is None:
        return redirect(url_for('docs'))
    elif bank_name != 'fred' and bank_name != 'boc':
        abort(400, description=f"Bank {bank_name} not found.")

    table_class = Fred_rates if bank_name == 'fred' else Boc_rates
    hide_none = False
    params = table_class.all_params
    table = {}

    result = session.query(table_class)

    if 'series' in request.args:
        req_series = request.args['series']
        params = req_series.split(',')

    if 'start_date' in request.args:
        start_date = request.args['start_date']
        result = result.where(table_class.date >= start_date)

    if 'end_date' in request.args:
        end_date = request.args['end_date']
        result = result.where(table_class.date <= end_date)

    if 'hide_none' in request.args and request.args['hide_none'] == 'true':
        hide_none = True

    if 'offset' in request.args:
        offset = request.args['offset']
        if int(offset) < 0:
            abort(400, "offset must not be negative.")
        result = result.offset(offset)

    if 'limit' in request.args:
        limit = request.args['limit']
        if int(limit) < 0:
            abort(400, "limit must not be negative.")
        result = result.limit(limit)

    for row in result:
        series = row.get_keys(params)
        date, *values = row.get_columns(series)
        r = {}
        for key, value in zip(series, values):
            if hide_none and value != None:
                r[key] = value
            elif not hide_none:
                r[key] = value
        table[date] = r

    return jsonify({f"{bank_name} data": table})

@app.errorhandler(400)
def api_request_error(err):
    """The handler for bad requests to the API."""
    return jsonify({'error': f"{err}"}), 400

connected = True

if __name__ == '__main__':
    try:
        engine = create_engine(DB_URI)
    except:
        connected = False
        print("Could not connect to database.")
    app.run()
