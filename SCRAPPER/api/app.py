from flask import Flask
import json

app = Flask(__name__)


@app.route('/')
def hello():
  return "Hello"


@app.route("/news")
def give_feed():
  with open('conten.json', 'r') as file:
    data = json.load(file)
  return data
