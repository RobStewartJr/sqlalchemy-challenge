import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create session 
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"All Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-01-01<br/>"
        f"/api/v1.0/2016-01-01/2017-01-14"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]    

    # Calculate the date 1 year ago from today
    last_year = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    precip_scores = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year).all()
    precip_dict = dict(precip_scores)

    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    """Return a JSON list of stations from the dataset."""
    # Query stations
    results_stations =  session.query(Measurement.station).group_by(Measurement.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    # Calculate the date 1 year ago from today
    # The days are equal 366 so that the first day of the year is included
    last_year = dt.datetime.strptime(last_date, "%Y-%m-%d") - dt.timedelta(days=366)

    results_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).all()
    tobs_list = list(results_tobs)

    return jsonify(tobs_list)



@app.route("/api/v1.0/<start>")
def start(start=None):
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""

    start_query = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    start_query_list = list(start_query)
    return jsonify(start_query_list)

    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    
    start_end = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    start_end_list=list(start_end)
    return jsonify(start_end_list)


if __name__ == '__main__':
    app.run(debug=True)