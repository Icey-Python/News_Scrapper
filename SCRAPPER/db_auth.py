import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

#insert data to a table
def insert_to_table(table_name:str,value:dict | list)-> str:
    data, count = supabase.table(table_name).insert(value).execute()
    return f"{data,count}"

#fetch data from a table
def fetch_from_table(table_name:str):
    response = supabase.table(table_name).select("*").execute()
    return response


