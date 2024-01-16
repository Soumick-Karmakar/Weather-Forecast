# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 21:49:00 2023

@author: Soumick
"""
import requests
import pandas as pd
import json
import csv
from flask import Flask, render_template
import logging
from logging.handlers import RotatingFileHandler
import os
from config import Config

class API:
    
    def __init__(self, api):
        self.api = api
        self.d = None
    
    
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
    
    
    # Method for cleaning the data
    def clean_data(self):
        app.logger.info('Data processing started')
        lst = self.data['data']
        d = str(lst[0])
        d = d.replace("'","\"")
        d = d.replace("None","0")
        d = json.loads(d)
        di=d
        d={}
        for key in di:
            if isinstance(di[key],str) or isinstance(di[key],int):
                d[key]=di[key]
        d = str(d)      
        d = d.replace("'","\"")
        d = json.loads(d)
        self.d = [d]
        app.logger.info('Data processing is successful')
        return self.d


class CSV:
    
    def __init__(self,data):
        self.d = data
    
    
    # Method to change the json data into csv
    def JSON_to_CSV(self):
        # Processing the data into a pandas DataFrame.
        df = pd.DataFrame(self.d)
        # Saving the processed data into a CSV file.
        df.to_csv('data/data.csv',index=False)
        app.logger.info('Data saved into CSV file successfully')


   
app = Flask(__name__)

# Configuring the log file path and format
path = os.path.join(os.path.dirname(__file__), 'logs')
logFile = os.path.join(path,'app.log')
logFormat = '%(asctime)s [%(levelname)s] - %(message)s'
logging.basicConfig(filename=logFile, level=logging.DEBUG, format=logFormat)

# Adding a rotating file handler to manage log file size
handler = RotatingFileHandler(logFile, maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(logFormat))
app.logger.addHandler(handler)

app.config.from_object(Config)


@app.route('/')
def index():
    app.logger.info('Rendering display.html page...')
    return render_template('display.html')


@app.route('/get_data', methods=['GET'])
def get_data():
    api_key = app.config['API_KEY']
    my_api = API(api_key)
    app.logger.info('API object created')
    my_api.api_call()
    clean_data = my_api.clean_data()  # Call clean_data to process and set self.d
    my_csv = CSV(clean_data)          # Create an instance of CSV with the processed data
    my_csv.JSON_to_CSV()              # Access self.d and create CSV
    
    # Read data from the CSV file
    app.logger.info('Reading data from CSV...')
    with open('data/data.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        data = list(csv_reader)
    app.logger.info('Rendering display.html page with loaded data...')
    return render_template('display.html', data = data)



if __name__ == '__main__':
    
    app.logger.info('Starting the application...')
    app.run(debug=True, port=5500)    # Running the Flask Application and selecting my desired port.
