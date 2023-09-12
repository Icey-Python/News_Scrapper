from flask import Flask
import json

app = Flask(__name__,static_folder="static")


@app.route('/')
def hello():
  return "Hello"


@app.route("/news")
def give_feed():
  with open('static/content.json', 'r') as file:
    data = json.load(file)
    return data


if __name__ == '__main__':
   app.run()