# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 21:49:00 2023

@author: Soumick
"""
# IMPORTS
#######################################################
import requests
import json
from flask import Flask, render_template
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Weather_1, City_2
from pymongo import MongoClient
########################################################


# API Class for API Calls and Data Cleaning
###############################################################################
class API:

    def __init__(self, api):
        self.api = api
        self.data = None

    # Method for calling API

    def api_call(self):
        try:
            app.logger.info('API call started')
            # Making a get request to the API.
            response = requests.get(self.api)
            if response.status_code == 200:
                # Fetching the data from the API in JSON format.
                self.data = response.json()
                app.logger.info('API call is successful')
            else:
                err_msg = 'Request failed with status code: ' + response.status_code
                app.logger.error(err_msg)
                print(f'Request failed with status code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            app.logger.error(e)
            print(f'Request failed with error {e}')

    # Method for cleaning the weather data

    def clean_data(self):
        app.logger.info('Data processing started')
        lst = self.data['data']
        data_str = str(lst[0]).replace("'", "\"").replace("None", "0")
        data_dic = json.loads(data_str)
        data = {}
        for key in data_dic:
            if isinstance(data_dic[key], str) or isinstance(data_dic[key], int):
                data[key] = data_dic[key]
        data_str = str(data).replace("'", "\"")
        data_JSON = json.loads(data_str)
        self.data = [data_JSON]
        app.logger.info('Data processing is successful')
        return self.data

    # Method for cleaning the city data

    def clean_data2(self):
        app.logger.info('Data processing started')
        lst = self.data["data"]
        my_list = []
        for i in lst:
            if (i['city'] == 'Delhi') or (i['city'] == 'Kolkata (Calcutta)') or (i['city'] == 'Bangalore') or (i['city'] == 'Hyderabad'):
                p = i['populationCounts'][0]
                if i['city'] == 'Kolkata (Calcutta)':
                    p['city'] = 'Kolkata'
                else:
                    p['city'] = i['city']
                my_list.append(p)
                if len(my_list) == 4:
                    break
        return my_list
###############################################################################


# mongo class to store and fetch data from mongo
###############################################################################
class mongo:

    def __init__(self, collections):
        self.c = collections

    # Method to store the json data into mongodb
    def store_data(self, data):
        self.c.insert_many(data)
        app.logger.info("Data successfully pushed into mongo")

    # Method to fetch data from mongodb
    def fetch_data(self):
        data_from_mongo = list(self.c.find({}))
        return data_from_mongo
###############################################################################


# Flask Application
###############################################################################
app = Flask(__name__)

# Configuring the log file path and format
path = os.path.join(os.path.dirname(__file__), 'logs')
logFile = os.path.join(path, 'app.log')
logFormat = '%(asctime)s [%(levelname)s] - %(message)s'

# Adding a rotating file handler to manage log file size
handler = RotatingFileHandler(logFile, maxBytes=10000, backupCount=1, delay=True)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(logFormat))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)  # or logging.DEBUG

# Loading configuration settings into the application
app.config.from_object(Weather_1)
app.config.from_object(City_2)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['AppDB']
wc = db['Weather']      # wc - weather collection
cc = db['City']         # cc - city collection
mc = db['Merge']        # mc - merge collection
###############################################################################


# Routes
###############################################################################
@app.route('/')
def index():
    app.logger.info('Rendering display.html page...')
    return render_template('display.html')


@app.route('/API_call', methods=['GET'])
def API_call():
    global db
    global wc            # wc - weather collection
    global cc            # cc - city collection
    global weather_data
    global city_data

    # Weather API calling
    weatherAPI = app.config['API_KEY_1']            # Weather API key fetched
    my_api = API(weatherAPI)
    my_api.api_call()
    # Call clean_data to process weather data
    clean_data = my_api.clean_data()
    mongo(wc).store_data(clean_data)                # Pushed data into mongo
    app.logger.info('Data inserted in collection: Weather')
    # Fetching the data from MongoDB
    weather_data = mongo(wc).fetch_data()
    app.logger.info('Data fetched from collection: Weather')

    # City API calling
    cityAPI = app.config['API_KEY_2']               # City API key fetched
    my_api = API(cityAPI)
    my_api.api_call()
    # Call clean_data2 to process city data
    clean_data = my_api.clean_data2()
    mongo(cc).store_data(clean_data)                # Pushed data into mongo
    app.logger.info('Data inserted in collection: City')
    # Fetching the data from MongoDB
    city_data = mongo(cc).fetch_data()
    app.logger.info('Data fetched from collection: City')

    return render_template('display.html', data1=weather_data, data2=city_data)


@app.route('/merge', methods=['GET'])
def merge():
    global db
    global wc            # wc - weather collection
    global cc            # cc - city collection
    global mc            # mc - merge collection
    global weather_data
    global city_data

    # Defining the aggregation pipeline
    pipeline = [
        {
            "$lookup": {
                "from": "City",
                "localField": "city_name",
                "foreignField": "city",
                "as": "city_data"
            }
        },
        {
            "$unwind": {
                "path": "$city_data",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$replaceRoot": {"newRoot": {"$mergeObjects": ["$$ROOT", "$city_data"]}}
        },
        {
            "$project": {"_id": 0}  # Excluding _id field
        }
    ]
    mc.insert_many(wc.aggregate(pipeline))     # Pushed merged data into mongo
    app.logger.info('Aggregated is successfully pushed into mongo')
    merge_data = mongo(mc).fetch_data()        # Fetched merged data from mongo
    app.logger.info('Aggregated is successfully fetched from mongo')
    return render_template('display.html', data1=weather_data, data2=city_data, data3=merge_data)

###############################################################################


if __name__ == '__main__':

    app.logger.info('Starting the application...')
    # Running the Flask Application and selecting my desired port.
    app.run(debug=True, port=5500)
