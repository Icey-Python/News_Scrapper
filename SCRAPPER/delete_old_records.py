from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime,timedelta
import os
load_dotenv()

url= os.environ.get("SUPABASE_URL")
key= os.environ.get("SUPABASE_KEY")
supabase_client = create_client(url,key)
print(url,key)

def delete_old_records():
    # Delete records older than 3 days
    three_days_ago = datetime.now() - timedelta(days=3)
    res = supabase_client.table("news_content").delete().lt("sort_data", three_days_ago.isoformat()).execute()

    print(f"Deleted {res} old records")

delete_old_records()