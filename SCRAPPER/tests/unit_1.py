import os
from supabase import create_client,Client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY') 
supabase: Client = create_client(url, key)

# Query data
data = supabase.table('news_content').select('*').execute().data

from datetime import datetime

articles = data

def get_datetime(article):
  return datetime.strptime(article['sort_data'], '%Y-%m-%dT%H:%M:%SZ') 
try:
    sorted_articles = sorted(articles, key = lambda x: x['sort_data'])
    #for article in sorted_articles:
            #print(article['title'], article['sort_data'])
    print(sorted_articles)

except ValueError:
    pass


