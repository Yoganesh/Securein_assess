from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uvicorn

from db import weather_collection
from data_transform import transform_data

app = FastAPI()

class WeatherResponse(BaseModel):
    date: str
    temp_min: float
    temp_max: float
    temp_avg: float
    humidity_avg: float
    pressure_avg: float
    heat_index_avg: float

class YearlyStatsResponse(BaseModel):
    month: int
    temp_min: float
    temp_max: float
    temp_median: float

transform_data()

@app.get("/weather", response_model=list[WeatherResponse])
def get_weather_data(page_offset: Optional[int] = None, month: Optional[int] = None, date: Optional[str] = None):
    query = {}

    if date:
        try:
            query['datetime_utc'] = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    elif month:
        if page_offset == None:
            raise HTTPException(status_code=400, detail="Page offset is needed if you are querying for month")
        if 1 <= month <= 12:
            query = {'$expr': {'$eq': [{'$month': '$datetime_utc'}, month]}}
        else:
            raise HTTPException(status_code=400, detail="Invalid month. It should be between 1 and 12.")

    else:
        raise HTTPException(status_code=400, detail="Either date or month must be provided.")

    if date:
        result = list(weather_collection.find(query))
    else:
        result = list(weather_collection.find(query).skip(page_offset).limit(20))

    if not result:
        raise HTTPException(status_code=404, detail="No weather data found.")

    return [{"date": x['datetime_utc'].strftime("%Y-%m-%d"),
             "temp_min":x['temp_min'],
             "temp_max":x['temp_max'],
             "temp_avg":x['temp_avg'],
             "humidity_avg":x['humidity_avg'],
             "pressure_avg":x['pressure_avg'],
             "heat_index_avg":x['heat_index_avg']
             } for x in result]


@app.get("/weather/statistics", response_model=list[YearlyStatsResponse])
def weather_stats_year(year: int):
    pipeline = [
        {"$match": {"$expr": {"$eq": [{"$year": "$datetime_utc"}, year]}}},
        {"$group": {
            "_id": {"month": {"$month": "$datetime_utc"}},
            "temp_min": {"$min": "$temp_min"},
            "temp_max": {"$max": "$temp_max"},
            "temp_median": {"$avg": "$temp_avg"}
        }},
        {"$sort": {"_id.month": 1}}
    ]

    result = list(weather_collection.aggregate(pipeline))

    if not result:
        raise HTTPException(status_code=404, detail="No statistics found for the given year.")

    return [{"month": r['_id']['month'], "temp_min": r['temp_min'], "temp_max": r['temp_max'],
             "temp_median": r['temp_median']} for r in result]



if __name__ == "__main__":
    uvicorn.run(app)
