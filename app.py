import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base=automap_base()
Base.prepare(engine,reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station

app=Flask(__name__)

@app.route("/")
def welcome():
    return (
        f"Choices available:"
        f"  /api/v1.0/precipitaion"
        f"  /api/v1.0/Stations"
        f"  /api/v1.0/tobs"
        f"  /api/v1.0/<start>"
        f"  /api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    sbydate=session.query(Measurement).order_by(Measurement.date.desc()).first()
    year=int(sbydate.date[0:4])
    month=int(sbydate.date[5:7])
    day=int(sbydate.date[8:10])
    query_date=dt.date(year,month,day)-dt.timedelta(days=365)
    query_period=session.query(Measurement.date,Measurement.prcp).\
                    filter(Measurement.date >= str(query_date)).\
                    filter(Measurement.prcp != "NaN").\
                    order_by(Measurement.date.desc()).all()
    query_df=pd.DataFrame(query_period, columns=['Date','Precipitation'])
    query_by_df=query_df.groupby(['Date']).sum()
    query_api = query_by_df.to_dict()
    session.close()
    return jsonify(query_api)

@app.route("/api/v1.0/Stations")
def stations():
    session=Session(engine)
    station_list=session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session=Session(engine)
    sbydate=session.query(Measurement).order_by(Measurement.date.desc()).first()
    year=int(sbydate.date[0:4])
    month=int(sbydate.date[5:7])
    day=int(sbydate.date[8:10])
    query_date=dt.date(year,month,day)-dt.timedelta(days=365)
    highest_station=session.query(Measurement.station).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).first()
    highest_tobs=session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station==highest_station.station).\
                filter(Measurement.date>=query_date).all()
    session.close()
    return jsonify(highest_tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    session=Session(engine)
    start=str(start)
    start=start.replace('"','',2)
    year=int(start[6:10])
    month=int(start[0:2])
    day=int(start[3:5])
    start=dt.date(year,month,day)
    query=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= str(start)).\
                    order_by(Measurement.date.desc()).all()
    session.close() 
    return jsonify(query)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    return start, end

if __name__ == "__main__":
    app.run(debug=True)