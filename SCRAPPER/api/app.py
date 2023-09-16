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

def split_list(input_list, sublist_length):
    return [input_list[i:i + sublist_length] for i in range(0, len(input_list), sublist_length)]


content = []
@app.route("/news")
@cross_origin()  # enable CORS for this route
def give_feed():
  pageNo = request.args.get('page')
  list_data = supabase_client.table("news_content").select("*").order('sort_data',desc=True).execute().data
  
    # Create a set to keep track of distinct 'title' values
  distinct_titles = set()

  # Initialize an empty list to store the result
  result_list = []

  # Iterate through the original list of dictionaries
  for d in list_data:
      title = d['title']
      
      # Check if the 'title' is not in the set of distinct titles
      if title not in distinct_titles:
          # Add the dictionary to the result list
          result_list.append(d)
          
          # Add the 'title' to the set of distinct titles
          distinct_titles.add(title)


  content = split_list(result_list,50)
  pages = len(content) - 1
  if(pageNo):
    try:
      page = int(pageNo)
      # 'page' is now an integer
      try:
        return ({
      "page_count":pages,
      "content":content[page]
      })
      except IndexError:
        return {"error":f'invalid page number {page},valid page numbers are 0 to {len(content)-1}'}
    except (ValueError, TypeError):
      # 'page' is not a valid integer
      return {"error":"Page number is not an integer"}
  else:
    return ({
      "page_count":pages,
      "content":content[0]
      })

@app.route('/news/category/<category>')
@cross_origin()
def send_categories(category):
  # Data based on category
  try:
    categorical_data= supabase_client.table('news_content').select('*').order('sort_data',desc=True).eq('category',f'{category}').execute().data
        # Create a set to keep track of distinct 'title' values
    distinct_titles = set()

    # Initialize an empty list to store the result
    result_list = []

    # Iterate through the original list of dictionaries
    for d in categorical_data:
        title = d['title']
        
        # Check if the 'title' is not in the set of distinct titles
        if title not in distinct_titles:
            # Add the dictionary to the result list
            result_list.append(d)
            
            # Add the 'title' to the set of distinct titles
            distinct_titles.add(title)

    msg = result_list
  except:
    msg = "invalid category: check the categories using /news/categories"

  return {"content":msg}

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
      # Create a set to keep track of distinct 'title' values
  distinct_titles = set()

  # Initialize an empty list to store the result
  result_list = []

  # Iterate through the original list of dictionaries
  for d in res.data:
      title = d['title']
      
      # Check if the 'title' is not in the set of distinct titles
      if title not in distinct_titles:
          # Add the dictionary to the result list
          result_list.append(d)
          
          # Add the 'title' to the set of distinct titles
          distinct_titles.add(title)
  return {"message":"Fetched {} articles".format(len(list(result_list))-1)}

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
