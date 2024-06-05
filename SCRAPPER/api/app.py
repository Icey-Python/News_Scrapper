from flask import Flask, request, Response, jsonify
from flask_cors import CORS, cross_origin  # import CORS

import requests

import os,csv
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

CORS(app)  # enable CORS for whole app



@app.route('/')
@cross_origin()
def hello():
  return "hello documentation incoming!"


@app.route('/proxy-image')
@cross_origin()
def proxy_image():
  url = request.args.get('url')
  if(url):
    response = requests.get(url)
    image_data = response.content
    response_headers = {
        'Content-Type': response.headers['Content-Type'],
        'Access-Control-Allow-Origin': '*'
    }

    return Response(image_data, headers=response_headers)
  else:
    url = "https://pioneer-technical.com/wp-content/uploads/2016/12/news-placeholder.png"
    response = requests.get(url)
    image_data = response.content
    response_headers = {
        'Content-Type': response.headers['Content-Type'],
        'Access-Control-Allow-Origin': '*'
    }

    return Response(image_data, headers=response_headers)

def split_list(input_list, sublist_length):
    return [input_list[i:i + sublist_length] for i in range(0, len(input_list), sublist_length)]


content = []
@app.route("/news")
@cross_origin()
def give_feed():
    page = request.args.get('page', 0, type=int)
    try:
        with open('../articles.csv', 'r',encoding='utf-8') as file:
            # Create a CSV reader object
            reader = csv.DictReader(file)
            data = []
            # Iterate over each row in the CSV file
            for row in reader:
                # Append the row (as a dictionary) to the data list
                if(row['title']!= 'title'):
                    data.append(row)
            return jsonify({"content":data})
    except FileNotFoundError:
        print(os.getcwd())
        return {"error": "articles.csv file not found"}
    
     

def paginate(data, per_page=50):
    return [data[i:i+per_page] for i in range(0, len(data), per_page)]

@app.route('/news/category/<category>')
@cross_origin()
def send_categories(category):
    try:
        category_articles = []
        with open('../articles.csv', 'r', encoding='utf-8') as file:
            data = csv.DictReader(file)
            for row in data:
                if row['category'] == category:
                    category_articles.append(row)
            return jsonify({"content":category_articles})
    except FileNotFoundError:
        return {"error": "articles.csv file not found"}


@app.route('/news/categories')
@cross_origin()
def fetch_categories():
    try:
        categories = set()
        with open('../articles.csv', 'r', encoding='utf-8') as file:
            data = csv.DictReader(file)
            for row in data:
                categories.add(row['category'])
    except FileNotFoundError:
        return {"error": "articles.csv file not found"}

    return {"content": list(categories)}

@app.route('/news/count')
@cross_origin()
def get_count():
    try:
        with open('../articles.csv', 'r', encoding='utf-8') as file:
            data = list(csv.DictReader(file))
            return jsonify({"content":len(data)})
    except FileNotFoundError:
        return {"error": "articles.json file not found"}


#proxy weather from service
@app.route("/proxy_weather")
@cross_origin()
def get_weather_data():
  lat_long = request.args.get('q')
  weather_url = "http://api.weatherapi.com/v1/current.json?key=f305f994d74e46cc93290112231709&q={}".format(lat_long)
  if(lat_long):
    data = requests.get(weather_url).json()
    to_return = {
    "weather":{
      "is_day":data['current']['is_day'],
      "text":data['current']['condition']['text'],
      "icon":f"https:{data['current']['condition']['icon']}",
    "temp":data['current']['feelslike_c']
  }
  }
    return to_return
  else:
     return {'ERROR':'parameter q (lat,long) is required'} 

if __name__ == '__main__':
  app.run()

