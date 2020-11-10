import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

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
    return "precipitaion json"

@app.route("/api/v1.0/Stations")
def stations():
    return "stations json"

@app.route("/api/v1.0/tobs")
def tobs():
    return "tobs"

@app.route("/api/v1.0/<start>")
def start(start):
    return start

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    return start, end

if __name__ == "__main__":
    app.run(debug=True)