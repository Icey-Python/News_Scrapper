import os,json
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor


load_dotenv()
news_url = "https://nation.africa"
resp = requests.get(news_url)
soup = BeautifulSoup(resp.content, 'html.parser')

links = []
article_tags = []
article_links = []
articles_section = []
articles_content = []




def get_categories():
  #all links to all categories
  categories = soup.find_all('a', {'class': 'categories-nav_link'})
  with ThreadPoolExecutor(max_workers=20) as TPE:
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
  global article_links,article_tags,links
  get_categories()
  print('Categories Obtained')
  print('Categories: {}'.format(len(links)))
  with ThreadPoolExecutor(max_workers=200) as executor:
      executor.map(get_article_links,links[0:5])#request limiting

  print('articles obtained')

  article_tags = flatten_list(article_tags)
  print("Articles_before",len(article_tags))
  article_tags =list(set(article_tags))
  print("Article_tags after:",len(article_tags))

  with ThreadPoolExecutor(max_workers=20) as exec:
      exec.map(get_links, article_tags)



def get_content(link_object: dict):
    resp = requests.get(link_object['link'])
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        title = (soup.find('h1', {'class': 'title-medium'}).get_text()).strip()
    except AttributeError:
        title = ' '
    try:
        content = ""
        for paragraph in soup.find_all('div', {'class': 'paragraph-wrapper'}):
            content += (paragraph.get_text()).strip() + '\n\n'
    except AttributeError:
        content = ' '
    try:
        author = (soup.find('p', {'class': 'article-authors_authors'}).get_text()).strip()
    except AttributeError:
        author = 'anonymous'
    try:
        date_updated = (soup.find('time', {'class': 'date'}).get_text()).strip()
        date_tz = soup.find('time', {'class': 'date'})['datetime']  # 2023-09-14T04:19:30Z
    except AttributeError:
        date_updated = ''
        date_tz = '2023-09-14T04:19:30Z'
    try:
        image = "https://nation.africa" + soup.find('img', {
            'class': 'blk-img'
        }).get('src')
    except:
        image = ' '
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

    data_to_file = {
        "title": title,
        "content": content,
        "author": author,
        "date": date_updated,
        "image_url": image,
        "image_description": image_description,
        "category": category,
        "source": "Daily Nation",
        "sort_data": date_tz
    }

    # Write the data to a JSON file
    with open('articles.json', 'a', encoding='utf-8') as file:
        file.write(json.dumps(data_to_file, ensure_ascii=False) + '\n')

def get_content_main(data: list):
    with ThreadPoolExecutor(max_workers=10) as exec:
        exec.map(get_content, data)
    print(f"Content fetched and written to articles.json ({len(data)} articles)")

main()
get_content_main(article_links)

