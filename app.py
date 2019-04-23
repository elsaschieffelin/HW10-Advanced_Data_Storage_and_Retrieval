#Import everything!
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask
import datetime as dt
from datetime import timedelta
from flask import Flask, jsonify

#set up database
engine= create_engine("sqlite:///Resources/hawaii.sqlite")
sqlalchemy_database_uri = "sqlite:///Resources/hawaii.sqlite?check_same_thread=False"
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)
@app.route("/")
def home():
    print("Home page -- server request ... ")
    return (f"Welcome to home page! Check out these APIS! <br/>"
            f"Available routes:<br/>"
            f"/api/precipitation<br/>"
            f"/api/stations<br/>"
            f"/api/temperature<br/>"
            f"/api/<start><br/>"
            f"/api/<start>/<end>")
@app.route("/api/precipitation")
def api_precipitation(): 
    print ("api_precipitation -- server request ... ")
    #create query
    precipitation_query = session.query(Measurement.date, Measurement.prcp)
    prcp_dict = {}
    for date, prcp in precipitation_query: 
        prcp_dict.update({date: prcp})
    return jsonify(prcp_dict)
@app.route("/api/stations")
def api_stations(): 
    print("api_stations-- server request ... ")
    #query for all stations
    station_query = session.query(Station.station).all()
    station_list = []
    for i in station_query: 
        if i.station not in station_list:
            station_list.append(i.station)
    return jsonify(station_list)
@app.route("/api/temperature")
def api_temperature():
    print("api_temperature-- server request ... ")
    #find date parameters
    lastdate = session.query(Measurement.date)[-1]
    lastdate_dt = dt.datetime.strptime(lastdate.date, '%Y-%m-%d')
    yearago = lastdate_dt - dt.timedelta(days=365)
    #create query
    temperature_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= yearago)
    #store date and tobs in list (of dictionaries)
    temp_all = []
    for date,tobs in temperature_query: 
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_all.append(temp_dict)
    return jsonify(temp_all)
@app.route("/api/<start>")
def api_start(start):
    start_date = str(start) 
    tmin_query = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date)
    try:
        for i in tmin_query: 
            tmin = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return ('We do not have the proper information to supprt this query. Please select a different start date.')
    tmax_query = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date)
    try:
        for i in tmax_query: 
            tmax = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return ('We do not have the proper information to supprt this query. Please select a different start date.')
    tavg_query = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date)
    try:
        for i in tavg_query:
            tavg = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return ('We do not have the proper information to supprt this query. Please select a different start date.')
    start_stats = {}
    start_stats['TMIN'] = tmin
    start_stats['TMAX'] = tmax
    start_stats['TAVG'] = tavg
    return jsonify(start_stats)

@app.route('/api/<start>/<end>')
def api_rng(start, end): 
    start_date = str(start)
    end_date = str(end)
    tmin_query = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    try:
        for i in tmin_query: 
            tmin = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return (f'we do not have the proper information to support this query. Please select different dates.')
    tmax_query = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    try:
        for i in tmax_query: 
            tmax = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return (f'we do not have the proper information to support this query. Please select different dates.')
    tavg_query = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date)
    try:
        for i in tavg_query:
            tavg = i[0]
    except (sqlalchemy.exc.ProgrammingError):
        return (f'we do not have the proper information to support this query. Please select different dates.')
    rng_stats = {}
    rng_stats['TMIN'] = tmin
    rng_stats['TMAX'] = tmax
    rng_stats['TAVG'] = tavg
    return jsonify(rng_stats)
    
if __name__ == "__main__":
    app.run(debug=True)