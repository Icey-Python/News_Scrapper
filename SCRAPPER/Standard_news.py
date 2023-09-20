import requests
import datetime
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from str_to_timestamp import convert_to_timestamp_format as format_date
#get current time stamp
now = datetime.datetime.now()
start_time = int(now.timestamp() * 1000)
import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")

supabase_client= create_client(url, key)
data_to_auth = {
    "eventType": 1,
    "firstContentfulPaint": 3354,
    "firstPaint": 0,
    "location": "https://www.standardmedia.co.ke/",
    "memory": {},
    "pageloadId": "54ab9e01-70a1-48bb-b965-2e71a5342099",
    "referrer":
    "https://www.standardmedia.co.ke/sso/register?content=eyJpdiI6ImJQU1BwSjJDbVBwdnNEajcxL2N1QlE9PSIsInZhbHVlIjoicE54ejBDRjBOQVJlWGhYb1JGczhJQTFGZ2lWQ2EzQVVFdXk3c3l6dWlDVk0yQ28vTVdqQjNPZVUzcVB4RTlvVnAvUUZ0b0FKdGtnSElGVmhHUzZqR2hlWTZOaU5INGI3NEpWcE4zT0NRbTg9IiwibWFjIjoiMDFkYzRkNzBkNmNmNjFkMDc0MWM4MWY3NGIwYmQ5MmVkOWMxNWQwOTI5OTE4ZWQ2NTI2YTA1MjljNWU5ODc0MSIsInRhZyI6IiJ9",
    "resources": [],
    "siteToken": "aa625df50071416bb76b08dbdf5eec6b",
    "st": 2,
    "startTime": start_time,
    "timingsV2": {
        "connectEnd": 1384,
        "connectStart": 23,
        "decodedBodySize": 240389,
        "domainLookupEnd": 23,
        "domainLookupStart": 23,
        "domComplete": 5263,
        "domContentLoadedEventEnd": 4997,
        "domContentLoadedEventStart": 4981,
        "domInteractive": 4753,
        "duration": 5272,
        "encodedBodySize": 34207,
        "entryType": "navigation",
        "fetchStart": 23,
        "initiatorType": "navigation",
        "loadEventEnd": 5272,
        "loadEventStart": 5263,
        "name": "https://www.standardmedia.co.ke/",
        "nextHopProtocol": "h2",
        "redirectCount": 0,
        "redirectEnd": 0,
        "redirectStart": 0,
        "requestStart": 1385,
        "responseEnd": 2572,
        "responseStart": 2572,
        "secureConnectionStart": 1044,
        "serverTiming": [],
        "startTime": 0,
        "transferSize": 36480,
        "type": "reload",
        "unloadEventEnd": 2673,
        "unloadEventStart": 2630,
        "workerStart": 0
    },
    "versions": {
        "fl": "2023.8.0",
        "js": "2023.7.1",
        "timings": 2
    },
    "wd": 'false'
}
#required headers
headers_to_auth={
  "content-type":"application/json"
}
# Start a session
session = requests.Session()

# Website login URL
url = 'https://www.standardmedia.co.ke/cdn-cgi/rum'


# Make POST request to login
response = session.post(url, data=data_to_auth,headers=headers_to_auth)
print(response.status_code,response.text)

# Check if login was successful
if response.status_code == 200:
  print('Login successful')
else:
  print('Login failed')

# Now you can use the session to make other requests while logged in
response = session.get('https://www.standardmedia.co.ke')
data = response.content

#page content
categories = []
link_to_articles_by_category = []

#scraping logic
#get all categories from the menu
def get_news_categories():
    """Get all news categories from Standard Media KE"""
    soup = BeautifulSoup(data,'html.parser')
    main_menu = soup.find('nav',{'class':'navbar-light'}).find('div',{'class':'row'}).find('ul',{'class':'navbar-nav'}).find_all('li',{'class':'nav-item'})[0:9]
    
    for i in main_menu:
        name:str = (i.get_text()).strip().lower()
        link:str = i.find('a').get('href')
        categories.append({"category":name,"link":link})
    print(f"Obtained the following categories: {categories}, total({len(categories)})")
   

#Get all the article links for each category
def get_article_links_from_category(category_object:categories):
    """Get all articles of a specific category on standard media ke"""
    category = category_object['category']
    response = session.get(category_object['link'])
    data = response.content
    soup = BeautifulSoup(data,'html.parser')
    container = soup.find('section',{'class':'section-phase'})

    article_cards = container.select("div.card-body")

    for article_card in article_cards:
        link=article_card.select('a')[0]['href']  
        time = article_card.select('small.text-muted')[1].get_text()
        
        link_to_articles_by_category.append({"category":category,"link":link,"time":time})

    print("{} Links from {} category have been obtained".format(len(article_cards),category))


#create function that scrapes each category and returns articles as list of dicts with title, description & url
def get_single_page_content(page_obj:dict):
    print(page_obj['link'])
    page_content = requests.get(page_obj['link']).content
    soup = BeautifulSoup(page_content,'html.parser').select('div.col-md-8')[0]

    try:
        title = soup.select('div.col-md-8 .mb-4 > h1')[0].get_text()
        print(title)
    except AttributeError:
        title = ''
    
    try:
        content_body = soup.select('div.paywall p:not(.w-75)')
        paragraphs = []
        for i in content_body:
            text = i.get_text().replace('\n','').replace("SIGN UP"," ").replace("Subscribe to our newsletter"," ").replace("By clicking on the SIGN UP button, you agree to our Terms & Conditions and the Privacy Policy"," ").replace("By clicking on the   button, you agree to our Terms & Conditions and the Privacy Policy"," ").replace("Stay informed.", " ").strip()
            paragraphs.append(text)
        paragraphs = " ".join(map(str, paragraphs))
        paragraphs = paragraphs.split('.')
        
        updated_paragraphs = set()
        updated_paragraphs.update(paragraphs)
        paragraphs = "".join(updated_paragraphs)
    except AttributeError:
        paragraphs = ''
    try:
        image_link = soup.select("figure.image > img")[0]['src']
    except AttributeError:
        image_link =''
    try:
        image_description = soup.select("figure.image figcaption strong")[0].get_text()
    except AttributeError:
        image_description = ''
    try:
        author = soup.select("figure.image figcaption")[0].get_text()
    except AttributeError:
        author = ''

    category = (page_obj['category']).capitalize()    
    date_updated = format_date(page_obj['time'])
    source = "The standard"

    news_article_object = {
    "title": f"{title}",
    "content": f"{paragraphs}",
    "author": f"{author}",
    "date": f"{page_obj['time']}",
    "image_url": f"{image_link}",
    "image_description": f"{image_description}",  
    "category": f"{category}",
    "source": f"{source}",
    "sort_data":f"{date_updated}"
    }
    supabase_client.table("news_content").insert(news_article_object).execute()

def scrape():
    get_news_categories()
    with ThreadPoolExecutor(max_workers=25) as exec:
        exec.map(get_article_links_from_category,categories)

    #scrape content from the provided links from articles based on category
    with ThreadPoolExecutor(max_workers=25) as exec:
        exec.map(get_single_page_content,link_to_articles_by_category[0:3])
    # get_single_page_content(link_to_articles_by_category[0])
    