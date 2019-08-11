import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

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

session = Session(engine)

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Hello, these are the available api routes <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    precip=[Measurement.date,Measurement.prcp]
    precip_analysis= session.query(*precip).order_by(Measurement.date).all()

    precipitation_data = []

    for date, prcp in precip_analysis:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precipitation_data.append(precip_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def station():
    station_count=[Measurement.station]
    most_active=session.query(*station_count).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    return jsonify(list(most_active))

@app.route("/api/v1.0/tobs")
def tobs():
    last_date=session.query(Measurement.date).order_by(Measurement.date.desc()).first()    
    year=int(last_date[0][:4])
    day=int(last_date[0][-2:])
    month=int(last_date[0][5:last_date[0].index(f'-{day}')])
    last_year = dt.date(year,month,day) - dt.timedelta(days=365)

    last_12=[Measurement.tobs]
    
    last_twelve= session.query(*last_12).filter(Measurement.date>last_year).order_by(Measurement.date).all()
    
    return jsonify(list(last_twelve))

@app.route("/api/v1.0/<start>")
def start_date(start):
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    temp_data=list(temp_data)
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def range_temp(start, end):
    temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date.between(start,end)).all()
    temp_data = list(temp_data)
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)