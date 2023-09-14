import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from get_content import get_content_main
from db_auth import insert_to_table,fetch_from_table
news_url = "https://nation.africa"
resp = requests.get(news_url)
soup = BeautifulSoup(resp.content, 'html.parser')

links = []
article_tags = []
article_links = []
articles_section = []


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
    executor.map(get_article_links, links[0:3])

  print('articles obtained')

  article_tags = flatten_list(article_tags)

  with ThreadPoolExecutor(max_workers=200) as exec:
    exec.map(get_links, article_tags)
  print(article_links)
  insert_to_table('news_links',article_links)


  return article_links

