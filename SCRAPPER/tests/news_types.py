import requests

resp = requests.get('http://127.0.0.1:5000/news/category/Kenya@60')
print(resp.json())