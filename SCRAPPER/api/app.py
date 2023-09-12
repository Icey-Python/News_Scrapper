from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def hello():
  return "HEllo"
@app.route("/news")
def give_feed():
  return "json.load('content.json')"
