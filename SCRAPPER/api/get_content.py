import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from db_auth import fetch_from_table, insert_to_table
articles_content = []


def get_content(link_object:dict):
  global articles_content
  resp = requests.get(link_object['link'])
  soup = BeautifulSoup(resp.content, 'html.parser')
  title = (soup.find('h1', {'class': 'title-medium'}).get_text()).strip()

  content = ""
  for paragraph in soup.find_all('div', {'class': 'paragraph-wrapper'}):
    content+=(paragraph.get_text()).strip()+'\n\n'

  author = (soup.find('p', {'class': 'article-authors_authors'}).get_text()).strip()
  date_updated = (soup.find('time', {'class': 'date'}).get_text()).strip()
  image = "https://nation.africa" + soup.find('img', {
      'class': 'blk-img'
  }).get('src')
  image_description = (soup.find('figcaption', {
      'class': 'article-picture_caption'
  }).get_text()).strip()
  category = (soup.find('span', {
      'class': 'sub-nav_section-title-desktop'
  }).get_text()).strip()

  articles_content.append(
  {
      "title": f"{title}",
      "content": f"{content}",
      "author": f"{author}",
      "date": f"{date_updated}",
      "image_url": f"{image}",
      "image_description": f"{image_description}",  
      "category": f"{category}",
      "source": "Daily Nation"
  }
  )
def get_content_main(data:list):  
  with ThreadPoolExecutor(max_workers=200) as exec:
    exec.map(get_content, data)
  
  insert_to_table('news_content',articles_content)

  return (f"Parsed: {len(articles_content)}")

