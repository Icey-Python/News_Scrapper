from flask import Flask, request, Response
from flask_cors import CORS, cross_origin  # import CORS

import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# import os
# from supabase import create_client, Client
# from dotenv import load_dotenv
# load_dotenv()

news_url = "https://nation.africa"
resp = requests.get(news_url)
soup = BeautifulSoup(resp.content, 'html.parser')

links = []
article_tags = []
article_links = []
articles_section = []
articles_content = []

app = Flask(__name__)

CORS(app)  # enable CORS for whole app

# url: str = os.environ.get("SUPABASE_URL")
# key: str = os.environ.get("SUPABASE_KEY")

# supabase: Client = create_client(url, key)

# insert data to a table
# def insert_to_table(table_name:str,value:dict | list)-> str:
#     data, count = supabase.table(table_name).insert(value).execute()
#     return f"{data,count}"

# #fetch data from a table
# def fetch_from_table(table_name:str):
#     response = supabase.table(table_name).select("*").execute()
#     return response.data



def get_categories():
  #all links to all categories
  categories = soup.find_all('a', {'class': 'categories-nav_link'})
  with ThreadPoolExecutor(max_workers=200) as TPE:
    TPE.map(get_links_from_categories, categories)


def get_links_from_categories(category):
  global news_url
  links.append((news_url + category.get('href')))


def get_article_links(link):
  #find all the article links for each category
  global articles_section, article_tags
  resp = requests.get(link)
  article_soup = BeautifulSoup(resp.content, 'html.parser')
  tags = article_soup.find_all(
      'a', {'class': 'teaser-image-large'}) + article_soup.find_all(
          'a', {'class': 'teaser-image-left'}) + article_soup.find_all(
              'a', {'class': 'teaser-image-none'})
  article_tags.append(tags)


def flatten_list(list_to_flatten):
  flattened_list = [item for sublist in list_to_flatten for item in sublist]
  return flattened_list


def get_links(elem):
  article_links.append({"link": (news_url + elem.get('href'))})
  


def main():
  global article_tags
  get_categories()
  print('Categories Obtained')
  with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(get_article_links, links[0:3])#request limiting

  print('articles obtained')

  article_tags = flatten_list(article_tags)

  with ThreadPoolExecutor(max_workers=200) as exec:
    exec.map(get_links, article_tags)
  return article_links
  # insert_to_table('news_links',article_links)


def get_content(link_object:dict):
  resp = requests.get(link_object['link'])
  soup = BeautifulSoup(resp.content, 'html.parser')
  try:
    title = (soup.find('h1', {'class': 'title-medium'}).get_text()).strip()
  except AttributeError:
    title = ' '
  try:
    content = ""
    for paragraph in soup.find_all('div', {'class': 'paragraph-wrapper'}):
      content+=(paragraph.get_text()).strip()+'\n\n'
  except AttributeError:
    content = ' '
  try:
    author = (soup.find('p', {'class': 'article-authors_authors'}).get_text()).strip()
  except AttributeError:
    author = 'anonymous'
  try:
    date_updated = (soup.find('time', {'class': 'date'}).get_text()).strip()
    date_tz = soup.find('time', {'class': 'date'})['datetime'] #2023-09-14T04:19:30Z
  except AttributeError:
    date_updated = ''
    date_tz = '2000-01-00T00:00:00Z'
  try:
    image = "https://nation.africa" + soup.find('img', {
        'class': 'blk-img'
    }).get('src')
  except:
    image=' '
  try:
    image_description = (soup.find('figcaption', {
        'class': 'article-picture_caption'
    }).get_text()).strip()
  except AttributeError:
    image_description = ' '
  try:
    category = (soup.find('span', {
        'class': 'sub-nav_section-title-desktop'
    }).get_text()).strip()
  except AttributeError:
    category = "other"

  data_to_db ={
      "title": f"{title}",
      "content": f"{content}",
      "author": f"{author}",
      "date": f"{date_updated}",
      "image_url": f"{image}",
      "image_description": f"{image_description}",  
      "category": f"{category}",
      "source": "Daily Nation",
      "sort_data":date_tz
  }
  articles_content.append(data_to_db)

def get_content_main(data:list): 

  with ThreadPoolExecutor(max_workers=200) as exec:
    exec.map(get_content,data)

  # insert_to_table('news_content',articles_content)
  



@app.route('/')
@cross_origin()
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
  get_content_main(main())
  return articles_content
  

@app.route('/api/dev/update')
@cross_origin()
def update_news_feed():
  #update news feed 
  # - **add the return to this method below**
  # data_list = main()
  # get_content_main(data_list)

  
  return "Information fetched"



if __name__ == '__main__':
  app.run()
