import requests
from bs4 import BeautifulSoup
url = "https://phet.colorado.edu/sims/html/projectile-motion/latest/projectile-motion_all.html"

resp = requests.get(url).content

parsed_resp = BeautifulSoup(resp,'html.parser')
# simulation = parsed_resp.select("#sceneryTextSizeContainer")
# print(simulation)
with open('test.html','w') as file:
    file.write(str(parsed_resp))
# print(parsed_resp)
                                       

