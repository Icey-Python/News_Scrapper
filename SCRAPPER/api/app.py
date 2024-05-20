from flask import Flask, request, Response
from flask_cors import CORS, cross_origin  # import CORS

import requests

import os,json
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

CORS(app)  # enable CORS for whole app

url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")

supabase_client= create_client(url, key)



@app.route('/')
@cross_origin()
def hello():
  return "hello"


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
        with open('../../articles.json', 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
    except FileNotFoundError:
        return {"error": "articles.json file not found"}
    
    data = sorted(data, key=lambda x: x['sort_data'], reverse=True)
    content = paginate(data, per_page=50)
    try:
        results = content[page]
        return {
            "page_count": len(content) - 1,
            "content": results
        }
    except IndexError:
        return {"error": "Invalid page number"}


def paginate(data, per_page=50):
    return [data[i:i+per_page] for i in range(0, len(data), per_page)]

@app.route('/news/category/<category>')
@cross_origin()
def send_categories(category):
    try:
        with open('../../articles.json', 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
    except FileNotFoundError:
        return {"error": "articles.json file not found"}

    categorical_data = [d for d in data if d['category'].lower() == category.lower()]
    categorical_data = sorted(categorical_data, key=lambda x: x['sort_data'], reverse=True)

    # Create a set to keep track of distinct 'title' values
    distinct_titles = set()
    result_list = []

    # Iterate through the original list of dictionaries
    for d in categorical_data:
        title = d['title']

        # Check if the 'title' is not in the set of distinct titles
        if title not in distinct_titles:
            # Add the dictionary to the result list
            result_list.append(d)

            # Add the 'title' to the set of distinct titles
            distinct_titles.add(title)

    return {"content": result_list}

@app.route('/news/categories')
@cross_origin()
def fetch_categories():
  # Category types
  categories= supabase_client.table('news_content').select('category').execute().data
  category_list = [d['category'] for d in categories]
  unique_categories = set(category_list)
  return list(unique_categories)

@app.route('/news/count')
@cross_origin()
def get_count():
    try:
        with open('../../articles.json', 'r', encoding='utf-8') as file:
            data = [json.loads(line) for line in file]
    except FileNotFoundError:
        return {"error": "articles.json file not found"}

    # Create a set to keep track of distinct 'title' values
    distinct_titles = set()
    result_list = []

    # Iterate through the original list of dictionaries
    for d in data:
        title = d['title']

        # Check if the 'title' is not in the set of distinct titles
        if title not in distinct_titles:
            # Add the dictionary to the result list
            result_list.append(d)

            # Add the 'title' to the set of distinct titles
            distinct_titles.add(title)

    return {"message": "Fetched {} articles".format(len(result_list))}

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

