from flask import Flask, request, Response
from flask_cors import CORS, cross_origin  # import CORS
import requests

from db_auth import fetch_from_table
from get_links import main
from get_content import get_content_main
app = Flask(__name__)

CORS(app)  # enable CORS for whole app


@app.route('/')
def hello():
  return "Hello"


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
  return fetch_from_table('news_content')
  

@app.route('/api/dev/update')
@cross_origin()
def update_news_feed():
  #update news feed 
  # - **add the return to this method below**
  data_list = main()
  get_content_main(data_list)
  
  return "Information fetched"



if __name__ == '__main__':
  app.run()
