from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['weather_db']
weather_collection = db['delhi_weather']