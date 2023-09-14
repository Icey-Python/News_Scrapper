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
  response = supabase_client.table("news_content").select("*").execute()
  return response.data
  

@app.route('/news/categories')
@cross_origin()
def send_categories():
  # update news feed 
  # - **add the return to this method below**
  categories = supabase_client.table('news_content').select('category').distinct().execute()
  return categories

@app.route('/news/count')
def get_count():
  count = len(requests.get('/news'))
  return "There are {} articles in the db".format(count)


if __name__ == '__main__':
  app.run()
