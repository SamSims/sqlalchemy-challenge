# Import the dependencies.

from flask import Flask, jsonify
import sqlalchemy
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return ("Welcome to the Home Page<br/>"
            "/api/v1.0/precipitation<br/>"
            "/api/v1.0/stations<br/>"
            "/api/v1.0/tobs<br/>"
            "/api/v1.0/yyyy-mm-dd<br/>"
            "/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    # dict of last 12 months of precip {date:precip}
    latestdate = session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    dateforcalc = latestdate.date.split('-')
    startdate = dt.date(int(dateforcalc[0]),int(dateforcalc[1]),int(dateforcalc[2])) - dt.timedelta(days=365)
    raindata = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date>=startdate)
    perdict = {}
    for x in raindata:
        perdict[x.date] = x.prcp
    return jsonify(perdict)

@app.route("/api/v1.0/stations")
def stations():
    #list of stations
    stations = session.query(Station.station).all()
    starray = []
    for s in stations:
        starray.append(s.station)
        statdict = {"Stations":starray}
    return jsonify(statdict)

@app.route("/api/v1.0/tobs")
def tobs():
    #list of date and precip from active station
    mostactive = session.query(Measurement.station,func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).first()
    mas = mostactive[0]
    temps = session.query(Measurement.date,Measurement.tobs).filter(Measurement.station == mas).all()
    perdict = {}
    for x in temps:
        perdict[x.date] = x.tobs
    return jsonify(perdict)

@app.route("/api/v1.0/<start>")
def onlystart(start):
    #min, max, avg temp after date
    try:
        dateforcalc = start.split('-')
        startdate = dt.date(int(dateforcalc[0]),int(dateforcalc[1]),int(dateforcalc[2]))
        raindata = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>=startdate).all()
        perdict ={"Min":raindata[0][0],"Max":raindata[0][1],"Mean":raindata[0][2]}
        return jsonify(perdict)
    except:
        return"Please enter a valid date in format yyyy-mm-dd"
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    #min, max, avg temp between dates
    try:
        dateforcalc = start.split('-')
        startdate = dt.date(int(dateforcalc[0]),int(dateforcalc[1]),int(dateforcalc[2]))
        dateforcalc = end.split('-')
        enddate = dt.date(int(dateforcalc[0]),int(dateforcalc[1]),int(dateforcalc[2]))
    except:
        return"Please enter a valid date range in format yyyy-mm-dd"
    
    if(startdate>enddate):
        return "Date range invalid please enter a start date that is before the end date"
    else:    
        raindata = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date>=startdate).filter(Measurement.date<=enddate)
        perdict ={"Min":raindata[0][0],"Max":raindata[0][1],"Mean":raindata[0][2]}
        return jsonify(perdict)
    
if __name__ == "__main__":
    app.run(debug=True)