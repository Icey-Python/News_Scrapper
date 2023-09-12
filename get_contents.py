import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

news_url = "https://nation.africa"
content_data={}
#read the data and pass it for exctraction
def load_to_parser():
  import json
  # Load JSON data
  with open('links.json') as f:
    data = json.load(f) 
    content_data = {}.fromkeys(data, [])
    print(content_data)
  # Extract lists from each key  
  for key, value in data.items():
    links = value[0:5]
    with ThreadPoolExecutor(max_workers=200) as executor:
      executor.map(get_content_from_articles,links)
    
#exctract articles links from a dict
def get_content_from_articles(link:str)->None:
  global news_url,content_data
  
  resp = requests.get(link)
  data = BeautifulSoup(resp.content,'html.parser')
  category = (data.find('span',{'class':'sub-nav_section-title-desktop'}).get_text()).strip()
  title = (data.find('h1',{'class':'title-medium'}).get_text()).strip()
  time_updated = (data.find('time',{'class':'date'}).get_text()).strip()

  image = news_url + (data.find('img',{'class':'blk-img'}).get('src'))
  author = (data.find('p',{'class':'article-authors_authors'}))
  content=[]
  for paragraph in data.find_all('div',{'class':'paragraph-wrapper'}):
    content.append(paragraph.get_text()).strip()
  article_data = {
    'category': category,
    'title': title,
    'time_updated': time_updated, 
    'image': image,
    'content': content
  }
  print(article_data)
  (content_data[category]).append(article_data)

load_to_parser()