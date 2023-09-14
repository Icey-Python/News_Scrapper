import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from db_auth import fetch_from_table, insert_to_table
articles_content = []


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

  insert_to_table('news_content',articles_content)
  