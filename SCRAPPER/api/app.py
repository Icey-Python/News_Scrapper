from flask import Flask, request, Response
from flask_cors import CORS, cross_origin  # import CORS

import requests

import os
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


@app.route("/news")
@cross_origin()  # enable CORS for this route
def give_feed():
  from datetime import datetime
  response = supabase_client.table("news_content").select("*").order('sort_data',desc=True).limit(100).execute().data
  # Sort the list in descending order based on the 'sort_data' key
 
  return response

@app.route('/news/category/<category>')
@cross_origin()
def send_categories(category):
  # Data based on category
  try:
    categorical_data= supabase_client.table('news_content').select('*').order('sort_data',desc=True).limit(100).eq('category',f'{category}').execute().data
    msg = categorical_data
  except:
    msg = "invalid category: check the categories using /news/categories"

  return msg

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
  #articles count
  res = supabase_client.table('news_content').select('*',count='exact').execute()
  return "Fetched {} articles".format(res.count)

#proxy loc data from service
@app.route("/proxy_location/<key>")
@cross_origin()
def proxy_data(key):
  loc = request.args.get('q')
  loc_key = request.args.get('location_key')
  if(len(key)>8):
    #get location key from coords
    if (loc != ''):
      resp = requests.get(f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?apikey={key}&q={loc}")
      data = resp.json()
    #get location weather
    else:
      data = 'parameter q is required'
  else:
    data = "Please Enter a valid key"
  return data

#proxy weather from service
@app.route("/proxy_weather/<loc_key>")
@cross_origin()
def get_weather_data(loc_key):
  key = request.args.get('api_key')
  print(loc_key,key)
  if(loc_key):
        resp = requests.get(f"https://dataservice.accuweather.com/currentconditions/v1/{loc_key}?apikey={key}")
        data = resp.json()
  else:
    data = "You did not pass in a required parameter"
  return data

if __name__ == '__main__':
  app.run()
