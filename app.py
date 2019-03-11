import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import pandas as pd
import numpy as np
from flask import Flask, jsonify
import datetime as dt

# Flask Setup
app = Flask(__name__)
engine = create_engine("sqlite:///Resources_HW/hawaiiV2.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

# Create home
# url: http://127.0.0.1:5000/

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()

    # Save the query results as a Pandas DataFrame and set the index to the date column
    results_df = pd.DataFrame(results, columns=['date', 'precipitation'])
    results_df.set_index('date', inplace=True)

    # Sort the dataframe by date
    results_df = results_df.sort_values(by='date', ascending=True)
    
    # Convert df to dictionary
    results_df_dict = results_df.reset_index().to_dict('records')

    return jsonify(results_df_dict)

@app.route("/api/v1.0/stations")
def stations():
    # All stations
    all_stations = session.query(Station.station).all()

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the dates and temperatures
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year).all()
    # results

    # Save the query results as a Pandas DataFrame and set the index to the date column
    results_df = pd.DataFrame(results, columns=['date', 'temperature'])
    results_df.set_index('date', inplace=True)

    # Sort the dataframe by date
    results_df = results_df.sort_values(by='date', ascending=True)
    
    # Convert df to dictionary
    results_df_dict = results_df.reset_index().to_dict('records')

    return jsonify(results_df_dict)

@app.route("/api/v1.0/<start>")
def start(start=None):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    group_by(Measurement.date).all()

    return jsonify(from_start)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):

    between_start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date <= end).\
    group_by(Measurement.date).all()

    return jsonify(between_start_end)

if __name__ == "__main__":
    app.run(debug=True)