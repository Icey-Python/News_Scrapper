import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

news_url = "https://nation.africa"
resp_data = requests.get(news_url)

categories = []
category_tags = []
articles_links={}


#getting the categories from the menu
def get_categories():
  global resp_data, categories
  soup = BeautifulSoup(resp_data.content, 'html.parser')
  category_list = soup.find_all('li', {'class': 'col-1-1'})
  categories = category_list


#crawling the categories to discover urls for the various categories
def crawl_categories(category) -> None:
  global category_tags
  category_title = (category.find('a', {
      'class': 'categories-nav_title'
  }).get_text()).strip()

  anchor_tags = category.find_all('a', {'class': 'categories-nav_link'})
  category_obj = {f"{category_title}": sort_links(anchor_tags)}
  category_tags.append(category_obj)


#sorting the links to their specific categories and prepend the base url to the link -> List of all links obtained for the various categories

def sort_links(anchor_tags_list:list) -> list:
  links = []
  for i in anchor_tags_list:
    link = i.get('href')
    links.append(news_url + link)
  return links


#crawl the links and for each category get links to articles
def get_articles_from_link(categories_list: dict) -> None:
  global articles_links
  category_title = list(categories_list.keys())[0]

  articles_links |= {category_title:[]}
  content_data =articles_links
  category_links = list(categories_list.values())[0]
  with ThreadPoolExecutor(max_workers=800) as executor:
    executor.map(get_category_articles, category_links)

#link to each article in a category
def get_category_articles(link:str) -> None:
  global news_url,articles_links

  resp = requests.get(link)
  article_soup = BeautifulSoup(resp.content, 'html.parser')
  title = (article_soup.find('span',{'class':'sub-nav_section-title-desktop'}).get_text()).strip()
 
  category_news_section = article_soup.find('section',
                                            {'class': 'teasers-row'})
  article_links_tags = category_news_section.find_all(
      'a', {'class': 'article-collection-teaser'})
  for article_link in article_links_tags:
   category_links_unparsed = []
   category_links_unparsed.append(news_url+article_link.get('href'))
   (articles_links[title]).append(category_links_unparsed)

def flatten_dict_values(d):
    result = {}
    for k, v in d.items():
        flattened = [item for sublist in v for item in sublist]
        result[k] = flattened
    return result


def scrape_for_news():
  get_categories()
  with ThreadPoolExecutor(max_workers=800) as executor:
    executor.map(crawl_categories, categories)
  with ThreadPoolExecutor(max_workers=800) as executor:
    executor.map(get_articles_from_link, category_tags)

  with open("links.json","w") as file:
    import json
    flattened_data = flatten_dict_values(articles_links)
    json.dump(flattened_data,file, indent=4)
  
  
    
scrape_for_news()
