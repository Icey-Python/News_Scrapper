from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime,timedelta
import os
load_dotenv()

url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")
print("data:",url, key,end='\n')

supabase_client= create_client(url, key)
print(url,key)

def delete_old_records():
    # Delete records older than 3 days
    one_day_ago = datetime.now() - timedelta(days=1)
    res = supabase_client.table("news_content").delete().lt("sort_data", one_day_ago.isoformat()).execute()

    print(f"Deleted {len(res.data)} old records")

delete_old_records()
