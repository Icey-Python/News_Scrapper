import os
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import logging

# Constants
news_url = "https://nation.africa"
output_file = 'articles.csv'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Functions
def get_categories(soup):
    categories = soup.find_all('a', {'class': 'categories-nav_link'})
    links =[news_url + category.get('href') for category in categories] 
    return links

def get_article_links(link):
    try:
        resp = requests.get(link, timeout=10)
        resp.raise_for_status()
        article_soup = BeautifulSoup(resp.content, 'html.parser')
        tags = article_soup.find_all('a', {'class': 'teaser-image-large'}) + \
               article_soup.find_all('a', {'class': 'teaser-image-left'}) + \
               article_soup.find_all('a', {'class': 'teaser-image-none'})
        return tags
    except requests.RequestException as e:
        logging.error(f"Error fetching article links from {link}: {e}")
        return []

def flatten_list(list_to_flatten):
    return [item for sublist in list_to_flatten for item in sublist]

articles_content= []
def get_content(link_object):
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
    
def save_articles_to_csv(data, filename=output_file):
    file_exists = os.path.isfile(filename) 

    with open(filename, 'a', encoding='utf-8', newline='') as file:
        fieldnames = ['title', 'content', 'author', 'date', 'image_url', 'image_description', 'category', 'source', 'sort_data']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)
    #remove duplicates every time on save
    df = pd.read_csv(filename)
    df_deduplicated = df.drop_duplicates(subset=['title'])
    df_deduplicated.to_csv(filename,index=False)

def sort_csv_by_timestamp(input_file):
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        sorted_rows = sorted(reader, key=lambda row: row['sort_data'], reverse=True)

    with open(input_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    logging.info('File sorted in timestamp order')

def main():
    resp = requests.get(news_url)
    soup = BeautifulSoup(resp.content, 'html.parser')
    links = get_categories(soup)
    logging.info('Categories Obtained')
    logging.info(f'Categories: {len(links)}')

    article_tags = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        article_tags_lists = list(executor.map(get_article_links,links))
        article_tags = flatten_list(article_tags_lists)
    logging.info('Articles obtained')
    logging.info(f"Articles before: {len(article_tags)}")
    article_tags = list(set(article_tags)) 
    logging.info(f"Article tags after: {len(article_tags)}")
    
    article_links = []
    for elem in article_tags:
        if 'http' in elem.get('href'):
            link = elem.get('href')
        else:
            link = news_url + elem.get('href')
        article_links.append({"link": link})

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(get_content, article_links)

    save_articles_to_csv(articles_content)
    logging.info(f"Content fetched and written to articles.csv ({len(articles_content)} articles)")

    sort_csv_by_timestamp(output_file)

if __name__ == "__main__":
    main()

