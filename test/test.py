from flask import Flask, request, jsonify, redirect, url_for, render_template, abort
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy import Column, String, Float
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

url = "http://127.0.0.1:5000/"

app = Flask(__name__, template_folder='template')
app.config["DEBUG"] = True

DB_URI = ''

#meta = MetaData()
engine = create_engine(DB_URI)
#meta.reflect(engine)

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

class Fred_rates(Base):
    """Federal Reserve rates."""
    __tablename__ = 'fred_rates'

    date = Column(String, primary_key=True)
    prime_rate = Column(Float(2))
    five_year_average_mortgage = Column(Float(2))
    fifteen_year_average_mortgage = Column(Float(2))
    thirty_year_average_mortgage = Column(Float(2))

Base.metadata.create_all(engine)
