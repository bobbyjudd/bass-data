import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

visited = set()
tournament_urls = set()
BASE_URL = "https://www.bassmaster.com/"
T_URL = "/results/tournaments"
url_stack = [BASE_URL]

while url_stack:
    print(url_stack[-1])
    visited.add(url_stack[-1])
    if url_stack[-1].startswith(T_URL) and url_stack[-1] not in tournament_urls:
        tournament_urls.add(url_stack[-1])
        with open("t_urls.txt" , "a") as f:
            f.write(url_stack[-1]+'\n')
            
    try:
        r = urllib.request.urlopen(urljoin(BASE_URL, url_stack[-1]))
    except:
        continue
    finally:
        url_stack.pop()

    page = r.read()
    soup = BeautifulSoup(page, 'html.parser')
    for link in soup.find_all('a'):
        url = link.get('href')
        if url and url.startswith('/') and url not in visited:
            url_stack.append(url)
