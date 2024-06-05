import os
import csv
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
news_url = "https://nation.africa"
resp = requests.get(news_url)
soup = BeautifulSoup(resp.content, 'html.parser')

def get_categories(soup):
    # all links to all categories
    categories = soup.find_all('a', {'class': 'categories-nav_link'})
    links = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        links = list(executor.map(lambda category: news_url + category.get('href'), categories))
    return links

def get_article_links(link):
    # find all the article links for each category
    article_tags = []
    resp = requests.get(link)
    article_soup = BeautifulSoup(resp.content, 'html.parser')
    tags = article_soup.find_all('a', {'class': 'teaser-image-large'}) + \
           article_soup.find_all('a', {'class': 'teaser-image-left'}) + \
           article_soup.find_all('a', {'class': 'teaser-image-none'})
    article_tags.extend(tags)
    return article_tags

def flatten_list(list_to_flatten):
    return [item for sublist in list_to_flatten for item in sublist]

def get_content(link_object):
    resp = requests.get(link_object['link'])
    soup = BeautifulSoup(resp.content, 'html.parser')
    try:
        title = soup.find('h1', {'class': 'title-medium'}).get_text().strip()
    except AttributeError:
        title = ''
    try:
        content = "\n\n".join([p.get_text().strip() for p in soup.find_all('div', {'class': 'paragraph-wrapper'})])
    except AttributeError:
        content = ''
    try:
        author = soup.find('p', {'class': 'article-authors_authors'}).get_text().strip()
    except AttributeError:
        author = 'anonymous'
    try:
        date_updated = soup.find('time', {'class': 'date'}).get_text().strip()
        date_tz = soup.find('time', {'class': 'date'})['datetime']  # 2023-09-14T04:19:30Z
    except AttributeError:
        date_updated = ''
        date_tz = '2023-09-14T04:19:30Z'
    try:
        image = "https://nation.africa" + soup.find('img', {'class': 'blk-img'}).get('src')
    except:
        image = ''
    try:
        image_description = soup.find('figcaption', {'class': 'article-picture_caption'}).get_text().strip()
    except AttributeError:
        image_description = ''
    try:
        category = soup.find('span', {'class': 'sub-nav_section-title-desktop'}).get_text().strip()
    except AttributeError:
        category = 'other'

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

    return data_to_file

def save_articles_to_csv(data, filename='articles.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', encoding='utf-8', newline='') as file:
        fieldnames = ['title', 'content', 'author', 'date', 'image_url', 'image_description', 'category', 'source', 'sort_data']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(data)

def sort_csv_by_timestamp(input_file):
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        sorted_rows = sorted(reader, key=lambda row: row['sort_data'], reverse=True)

    with open(input_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    print('File sorted in timestamp order')

def main():
    links = get_categories(soup)
    print('Categories Obtained')
    print('Categories: {}'.format(len(links)))

    article_tags = []
    with ThreadPoolExecutor(max_workers=200) as executor:
        article_tags_lists = list(executor.map(get_article_links, links))  # request limited to the first five
        article_tags = flatten_list(article_tags_lists)
    
    print('Articles obtained')
    print("Articles before:", len(article_tags))
    article_tags = list(set(article_tags))
    print("Article tags after:", len(article_tags))

    article_links = [{"link": news_url + elem.get('href')} for elem in article_tags]

    with ThreadPoolExecutor(max_workers=10) as executor:
        articles_content = list(executor.map(get_content, article_links))

    save_articles_to_csv(articles_content)
    print(f"Content fetched and written to articles.csv ({len(articles_content)} articles)")

    sort_csv_by_timestamp('articles.csv')

if __name__ == "__main__":
    main()

