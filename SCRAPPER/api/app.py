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
  response = supabase_client.table("news_content").select("*").execute().data
  # Sort the list in descending order based on the 'sort_data' key
 
  return response

@app.route('/news/category/<category>')
@cross_origin()
def send_categories(category):
  # Data based on category
  try:
    categorical_data= supabase_client.table('news_content').select('*').eq('category',category).execute().data
    msg = categorical_data
  except:
    msg = "invalid category: check the categories using /news/categories"

  return msg

@app.route('/news/categories')
@cross_origin()
def fetch_categories():
  # Category types
  categories= supabase_client.table('news_content').select('category').execute().data
  return [d['category'] for d in categories]

@app.route('/news/count')
@cross_origin()
def get_count():
  #articles count
  res = supabase_client.table('news_content').select('*',count='exact').execute()
  return "Fetched {} articles".format(res.count)


if __name__ == '__main__':
  app.run()
