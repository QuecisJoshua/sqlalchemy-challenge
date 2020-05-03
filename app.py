import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///Resources/hawaii.sqlite")


Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)



@app.route("/")
def welcome():
    return (
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-27<br/>"
        f"/api/v1.0/2016-08-27/2016-09-10<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_dates = []
    for date, prcp in results:
        dates_dict = {}
        dates_dict["date"] = date
        dates_dict["percipitation"] = prcp
        all_dates.append(dates_dict)

    return jsonify(all_dates)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Measurement.station).\
        group_by(Measurement.station).all()

    session.close()

    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_date = dt.datetime.strptime((session.query(Measurement.date).order_by(Measurement.date.desc()).first())[0],'%Y-%m-%d')
    target_date = dt.date((last_date).year-1, (last_date).month, (last_date).day)

    
    sel = [Measurement.station, func.count(Measurement.date)]
    station_data = session.query(*sel).\
        filter(Measurement.date >= target_date).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.date).desc()).all()
    station_max_id = station_data[0][0]

    
    sel = [Measurement.date, Measurement.tobs]
    tobs_data = session.query(*sel).\
        filter(Measurement.station == station_max_id).\
        filter(Measurement.date >= target_date).\
        order_by(Measurement.date).all()

    session.close()

    tobs_year = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = tobs
        tobs_year.append(tobs_dict)

    print(f"Total entries for station {station_max_id} for the period past {target_date} is {len(tobs_year)}.")
    return jsonify(tobs_year)



@app.route("/api/v1.0/<start>")
def start_date(start):
   

    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    temp_stats = session.query(*sel).\
        filter(Measurement.date >= start).all()

    session.close()

    tobs_start = []
    for minimum, maximum, avg in temp_stats:
        tobs_dict = {}
        tobs_dict["minimum Temp"] = minimum
        tobs_dict["maximum Temp"] = maximum
        tobs_dict["average Temp"] = round(avg,1)
        tobs_start.append(tobs_dict)

    return jsonify(tobs_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    temp_stats = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    tobs_start_end = []
    for minimum, maximum, avg in temp_stats:
        tobs_dict = {}
        tobs_dict["minimum Temp"] = minimum
        tobs_dict["maximum Temp"] = maximum
        tobs_dict["average Temp"] = round(avg,1)
        tobs_start_end.append(tobs_dict)

    return jsonify(tobs_start_end)

if __name__ == "__main__":
    app.run(debug=True)