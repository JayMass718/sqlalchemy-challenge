import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the SQLAlchemy HW App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        )


@app.route("/api/v1.0/precipitation")
def precipitation(date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query Measurements
    results = session.query(Measurement.date, Measurement.prcp).all()
    
    session.close()

    """Fetch the prcp data whose date matches 
    the path variable supplied by the user, or a 404 if not."""
    
    canonicalized = date.replace(" ", "").lower()
    prcp_data = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        prcp_data.append(measurement_dict)
        
        
        search_term = prcp_data["date"].replace(" ", "").lower()
        
        if search_term == canonicalized:
            return jsonify(measurement_dict["prcp"])

    return jsonify({"error": f"PRCP data for date {date} not found."}), 404


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)
    

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and temperature observations 
    # from a year from the last data point.
    results = session.query(Measurement.tobs, Measurement.date).\
        filter(Measurement.date >= '2016-08-23').all()
    
    session.close()
    
    # Return a JSON list of Temperature Observations (tobs)
    # for the previous year.

    temp_obs= []
    for tobs, date in results:
        measurement_dict = {}
        measurement_dict["tobs"] = tobs
        measurement_dict["date"] = date
        temp_obs.append(measurement_dict)

    return jsonify(temp_obs)


@app.route("/api/v1.0/<start>") 
def calc_temps(start_date):    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query minimum temperature, the average temperature, 
    # and the max temperature for a given start range.
   results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    # Return a calculation of the TMIN, TAVG, and TMAX 
    #for all dates greater than and equal to the start date.
    canonicalized = start_date.replace(" ", "").lower()
    date_temps = []
    for tobs, date in results:
        temps_dict_ = {}
        temps_dict["tobs"] = tobs
        temps_dict["date"] = date
        date_temps.append(temps_dict)
        search_term = date_temps["date"].replace(" ", "").lower()
        
        if search_term == canonicalized:
            return jsonify(date_temps)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start_date, end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query minimum temperature, the average temperature, 
    # and the max temperature for a given start-end range.
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    
    session.close()

    # Return a calculation of the TMIN, TAVG, and TMAX
    # for all dates between the start and end date inclusive.
    canonicalized = start_date.replace(" ", ""), end_date.replace(" ", "").lower()
    date_temps = []
    for tobs, date in results:
        temps_dict_ = {}
        temps_dict["tobs"] = tobs
        temps_dict["date"] = date
        date_temps.append(temps_dict)
        search_term = date_temps["date"].replace(" ", "").lower()
        
        if search_term == canonicalized:
            return jsonify(date_temps)
     

if __name__ == '__main__':
    app.run(debug=True)