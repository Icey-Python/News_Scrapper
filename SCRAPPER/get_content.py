import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

articles_content = []


def get_content(link):
  resp = requests.get(link)
  soup = BeautifulSoup(resp.content, 'html.parser')
  title = (soup.find('h1', {'class': 'title-medium'}).get_text()).strip()
  content = []
  for paragraph in soup.find_all('div', {'class': 'paragraph-wrapper'}):
    content.append((paragraph.get_text()).strip())
  author = soup.find('p', {'class': 'article-authors_authors'}).get_text()
  date_updated = soup.find('time', {'class': 'date'}).get_text()
  image = "https://nation.africa" + soup.find('img', {
      'class': 'blk-img'
  }).get('src')
  image_description = soup.find('figcaption', {
      'class': 'article-picture_caption'
  }).get_text()
  category = soup.find('span', {
      'class': 'sub-nav_section-title-desktop'
  }).get_text()
  article_data = {
      "title": title,
      "author": author,
      "content": content,
      "image": image,
      "image_description": image_description,
      "date": date_updated,
      "category": category
  }
  articles_content.append(article_data)

def get_content_main():
  with open('static/links.json', 'r') as file:
    import json
    data = json.load(file)[0:50]
  
  with ThreadPoolExecutor(max_workers=200) as exec:
    exec.map(get_content, data)
  
  with open('static/content.json', 'w') as file:
    import json
    json.dump(articles_content, file, indent=4)
    
get_content_main()