# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 21:49:00 2023

@author: Desktop
"""
import requests
import pandas as pd
import json
import csv
from flask import Flask, render_template

class API:
    
    def __init__(self, api):
        self.api = api
        self.d = None
    
    # Method for calling API
    def api_call(self):
        try:
            # Making a get request to the API.
            response = requests.get(self.api)
            if response.status_code == 200:
                # Fetching the data from the API in JSON format.
                self.data = response.json()
            else:
                print(f'Request failed with status code {response.status_code}') 
        except requests.exceptions.RequestException as e:
            print(f'Request failed with error {e}')
    
    # Method for cleaning the data
    def clean_data(self):
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


   
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('display.html')

@app.route('/get_data', methods=['GET'])
def get_data():
    # Read data from the CSV file
    with open('data/data.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        data = list(csv_reader)
    return render_template('display.html', data = data)

if __name__ == '__main__':
    
    api = "https://api.weatherbit.io/v2.0/current?key=38140cf0a4304397a1a1273a27fad080&city=Kolkata"
    my_api = API(api)
    #print('api called')
    my_api.api_call()
    clean_data = my_api.clean_data()  # Call clean_data to process and set self.d
    my_csv = CSV(clean_data)          # Create an instance of CSV with the processed data
    #print('before csv')
    my_csv.JSON_to_CSV()              # Access self.d and create CSV
    #print('after csv')
    app.run(debug=True, port=5500)    # Running the Flask Application and selecting my desired port.
