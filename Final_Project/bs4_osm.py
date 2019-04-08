from bs4 import BeautifulSoup
from pprint import pprint

with open('rochester_ny.osm', 'r', encoding='utf8') as f:
    soup = BeautifulSoup(f, 'xml')

nodess = soup.find_all('node')

x=5


[pprint(n.content) for n in nodess]
