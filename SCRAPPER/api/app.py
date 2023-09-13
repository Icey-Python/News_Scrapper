from flask import Flask
from flask_cors import CORS, cross_origin  # import CORS

import json
from os import path

app = Flask(__name__)

CORS(app)  # enable CORS for whole app


@app.route('/')
def hello():
  return "Hello"


@app.route("/news")
@cross_origin()  # enable CORS for this route
def give_feed():
  with open('static/content.json', 'r') as file:
    data = json.load(file)
  return data


if __name__ == '__main__':
  app.run()
