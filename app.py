import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func



# 1. import Flask
from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)



# =============================================================================
# # Home page tha lists all available routes
# =============================================================================
@app.route("/")
def get_homepage():
    return (
        f"Welcome to the Climate API!<br>"
        f"Available Routes are:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<'start'><br>"
        f"/api/v1.0/<'start'>/<'end'>"
       
    )


@app.route("/precipitation")
# =============================================================================
# Returns precipitation date and data in a jsonified dictionary format
# data = {'date': "prcp'}
# =============================================================================
def get_precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    prcp_data = session.query(*sel).filter(Measurement.date >= dt.date(2016, 8, 23)).all()
    data = []
    for i in prcp_data:
        prcp_dict = {}
        prcp_dict['date'] = i[0]
        prcp_dict['prcp'] = i[1]
        
        data.append(prcp_dict)
    
    session.close()
    return jsonify(data)
    

@app.route("/stations")
# =============================================================================
# Return a JSON list of stations from the dataset
# =============================================================================
def get_stations(): 
    
    station_list = []
    session = Session(engine)
    list_of_stations = session.query(Station.id, Station.station, Station.name).all()
    
    for i in list_of_stations:
        station_list.append(i)
    
    session.close()
    return jsonify(station_list)



@app.route("/tobs")
# =============================================================================
# Query the dates and temperature observations of the most active station for the last year of data
# Returns a JSON list of temperature observations (TOBS) for the year.
# =============================================================================
def get_temperature_oberservation_data():
    session = Session(engine)
    begin_date = dt.date(2016, 8, 23)
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)) \
    .group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    
    station_temp = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station) \
    .filter(Measurement.date >= begin_date).all()
    
    session.close()
    return jsonify(station_temp)


@app.route("/<start>")
def get_temp_range_date(start):
    
    tmp_list = []
    session = Session(engine)
    begin_date = dt.datetime.strptime(start, "%Y-%m-%d")
    begin_date = begin_date.date()
    
    TMIN = session.query(Measurement.date, func.min(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date).all()
    TAVG = session.query(Measurement.date, func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date).all()
    TMAX = session.query(Measurement.date, func.max(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date).all()
    
    for i in zip(TMIN, TAVG,TMAX):
        jsnList = {}
        jsnList['date'] = i[0][0]
        jsnList['TMIN'] = i[0][1]
        jsnList['TAVG'] = round(i[1][1],2)
        jsnList['TMAX'] = i[2][1]

        tmp_list.append(jsnList)
    
        
    
    session.close()
    return jsonify(tmp_list)


@app.route("/<start>/<end>")
def get_temp_start_and_stop_data(start, end):
    tmp_list = []
    session = Session(engine)
    begin_date = dt.datetime.strptime(start, "%Y-%m-%d")
    begin_date = begin_date.date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    end_date = end_date.date()
    
    TMIN = session.query(Measurement.date, func.min(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date, Measurement.date <= end_date).all()
    TAVG = session.query(Measurement.date, func.avg(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date, Measurement.date <= end_date).all()
    TMAX = session.query(Measurement.date, func.max(Measurement.tobs)).group_by(Measurement.date).filter(Measurement.date >= begin_date, Measurement.date <= end_date).all()
    
    for i in zip(TMIN, TAVG, TMAX):
        jsnList = {}
        jsnList['date'] = i[0][0]
        jsnList['TMIN'] = i[0][1]
        jsnList['TAVG'] = round(i[1][1],2)
        jsnList['TMAX'] = i[2][1]

        tmp_list.append(jsnList)
    
    session.close()
    return jsonify(tmp_list)



if __name__ == "__main__":
    app.run(debug=True)
