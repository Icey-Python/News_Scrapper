from flask import Flask
import json

app = Flask(__name__)


@app.route("/news")
def hello_world():
  return json.load('content.json')
