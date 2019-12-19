import numpy as np

import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite",  connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create APP
app = Flask(__name__)

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
date_last_twelve_months = dt.datetime.strptime(last_date, '%Y-%m-%d') - relativedelta(months=12)

# 3. Define what to do when a user hits the index route
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )



# 4. Define what to do when a user hits the /aboutapi/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'precipitation' page...")

    data_last_twelve_months = session.query(Measurement.date, Measurement.prcp, Measurement.station). \
    filter(Measurement.date >= date_last_twelve_months.strftime('%Y-%m-%d')).order_by(Measurement.date).all()
    
    precip_data = []
    for data in data_last_twelve_months:
        precip_dict ={data.date: data.prcp, "Station": data.station}
        precip_data.append(precip_dict)
    
    return jsonify(precip_data)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'station' page...")

    station_list = session.query(Measurement.station).distinct()

    return jsonify([station[0] for station in station_list])

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")

    data_last_twelve_months = session.query(Measurement.date, Measurement.tobs, Measurement.station). \
    filter(Measurement.date >= date_last_twelve_months.strftime('%Y-%m-%d')).order_by(Measurement.date).all()
    
    temp_data = []
    for data in data_last_twelve_months:
        temp_dict = {data.date: data.tobs, "Station": data.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)
    
@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'start' page...")

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).group_by(Measurement.date).all()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["TMIN"] = result[1]
        date_dict["TAVG"] = result[2]
        date_dict["TMAX"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print("Server received request for 'Start_End' page...")

    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).group_by(Measurement.date).all()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["TMIN"] = result[1]
        date_dict["TAVG"] = result[2]
        date_dict["TMAX"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)