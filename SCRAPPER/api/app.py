from flask import Flask, request, Response
from flask_cors import CORS, cross_origin  # import CORS
import requests
import json
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
  with open('static/content.json', 'r') as file:
    data = json.load(file)
  return data

@app.route("/api/dev/update")
@cross_origin()
def update_news_feed():
  get_content_main()
  return "content feched sucessfully"
  
if __name__ == '__main__':
  app.run()
