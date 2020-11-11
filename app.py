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
    return(
        f"<h1>Choices available:</h1><hr>"
        f"/api/v1.0/precipitaion<br>"
        f"/api/v1.0/Stations<br>"
        f"/api/v1.0/tobs<br>"
        f"<b>All following dates shall have mm-dd-yyyy format</b><br>"
        f"/api/v1.0/start date<br>"
        f"/api/v1.0/start date/end date<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)

# Get the latest date

    sbydate=session.query(Measurement).order_by(Measurement.date.desc()).first()

# Parse date from query above

    year=int(sbydate.date[0:4])
    month=int(sbydate.date[5:7])
    day=int(sbydate.date[8:10])

# Calculate query date

    query_date=dt.date(year,month,day)-dt.timedelta(days=365)

# Create query_period for the year

    query_period=session.query(Measurement.date,Measurement.prcp).\
                    filter(Measurement.date >= str(query_date)).\
                    filter(Measurement.prcp != "NaN").\
                    order_by(Measurement.date.desc()).all()

# Create dataframe from query_period

    query_df=pd.DataFrame(query_period, columns=['Date','Precipitation'])

# Total precipitation by Date for the query period

    query_by_df=query_df.groupby(['Date']).sum()

# Convert to a dictionary

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

# Sort in descending order and query the first record which will be the latest date in the dataset

    sbydate=session.query(Measurement).order_by(Measurement.date.desc()).first()

# Parse date

    year=int(sbydate.date[0:4])
    month=int(sbydate.date[5:7])
    day=int(sbydate.date[8:10])

# Calculate query date to perform query required

    query_date=dt.date(year,month,day)-dt.timedelta(days=365)

# Find the station with the most observations

    highest_station=session.query(Measurement.station).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).first()

# Find all the tobs for that station for the year

    highest_tobs=session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station==highest_station.station).\
                filter(Measurement.date>=query_date).all()
    session.close()
    return jsonify(highest_tobs)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start, end = ""):

# Test the format of the date entered.

    try:
        dt.datetime.strptime(start,"%m-%d-%Y")
    except ValueError:

# If format is incorrect return error message

        return("mm-dd-yyyy format is required.")

# Open session if format is correct and parse date into year, month, and day and convert into a date object--->start

    session=Session(engine)
    start=str(start)
    year=int(start[6:10])
    month=int(start[0:2])
    day=int(start[3:5])
    start=dt.date(year,month,day)

# Test to see if date entered is only the start date and perform the appropriate query and return json format of that query result

    if (end==""):
        query=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= str(start)).\
            order_by(Measurement.date.desc()).all()
    else:

# If end date was entered continue to test the format and parse date into year, month, and day and convert into a date object--->end

        try:
            dt.datetime.strptime(end,"%m-%d-%Y")
        except ValueError:

# If format is incorrect return error message

            return("mm-dd-yyyy format is required.")
        end=str(end)
        year=int(end[6:10])
        month=int(end[0:2])
        day=int(end[3:5])
        end=dt.date(year,month,day)

# Perform query with start and end dates and return json format of the query result

        query=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
            filter(Measurement.date >= str(start)).\
            filter(Measurement.date <= str(end)).\
            order_by(Measurement.date.desc()).all()
    session.close() 
    return jsonify(query)

if __name__ == "__main__":
    app.run(debug=True)