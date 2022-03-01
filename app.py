import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
#import datetime as dt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

##### Database Setup #####
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create our session (link) from Python to the DB
session = Session(engine)



##### Flask setup #####
app = Flask(__name__)
##### Flask Routes #####

@app.route("/")
def welcome():
     """List all available API routes."""

     return("""<html>

     <h1>Welcome to list of all API routes of Honolulu, Hawaii Climate Analysis: </h1>
     <ul>
     <br>
     <li>
     Precipitations from the last 12 months of data in a dictionary:
     <br>
     <a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a>
     </li>
     <br>
     <li>
     JSON list of stations from the dataset:
     <br>
     <a href="/api/v1.0/stations">/api/v1.0/stations</a>
     </li>
     <br>

     <li>
     JSON list of Temperature Observations (tobs) for the last 12 months of data:
     <br>
     <a href="/api/v1.0/tobs">/api/v1.0/tobs</a>
     </li>
     <br>
     <li>
     JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided:
     <br>
     <a href="/api/v1.0/2017-04-26">/api/v1.0/2017-04-26</a>
     </li>
     <br>
     <li>
     Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive:
     <br>
     <a href="/api/v1.0/2017-04-26/2017-04-30">/api/v1.0/2017-04-26/2017-04-30</a>
     </li>
     <br>
     </ul>
     </html>
     """
     )     

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Docstring
    """Return a list of precipitations from last year"""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    latest_date = latest_date[0]


    # create a datetime object of latest_date
    latest_date_obj = datetime.strptime(latest_date, '%Y-%m-%d')

    # calculate the date 1 year ago from latest date
    last_year_date = (latest_date_obj - relativedelta(years=1)). strftime("%Y-%m-%d")

    # perform a query to retrieve the data and precipitation 
    prcp_12_last = session.query(Measurement.date, Measurement.prcp).\
                   filter(Measurement.date >= last_year_date).filter(Measurement.date <= latest_date).order_by(Measurement.date).all()
    
    # Convert list of tuples into normal list
    prcp_dict = dict(prcp_12_last)
    return jsonify(prcp_dict)

session.close()

@app.route("/api/v1.0/stations")
def stations():
    # Docstring
    """Return a JSON list of stations from the dataset."""
    # Query stations
    results_stations =  session.query(Station.station).all()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results_stations))

    return jsonify(stations_list)

session.close()

@app.route("/api/v1.0/tobs")
def tobs():
    # Docstring
    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the first element of the tuple
    latest_date = latest_date[0]

    # create a datetime object of latest_date
    latest_date_obj = datetime.strptime(latest_date, '%Y-%m-%d')

    # calculate the date 1 year ago from latest date
    last_year_date = (latest_date_obj - relativedelta(years=1)). strftime("%Y-%m-%d")

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year_date).all()

    

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps)
session.close()
    

@app.route("/api/v1.0/<start>")
def start(start=None):

    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided"""
    from_start = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start).group_by(Measurement.date).all()
    from_start_list=list(np.ravel(from_start))
    return jsonify(from_start_list)
session.close()


@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    # Docstring
    """Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive"""
    between_dates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    between_dates_list=list(np.ravel(between_dates))
    return jsonify(between_dates_list)

session.close()

if __name__ == '__main__':
    app.run(debug=True)