import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
import threading
import time
from bs4 import BeautifulSoup
import redis

r = redis.Redis(
    host='localhost',
    port=6379)

BASE_URL = "https://www.bassmaster.com/"
T_URL = "/results/tournaments"
NUM_THREADS = 20

def valid_search_url(search_url):
    return (search_url and
            search_url.startswith('/') and
            not search_url.startswith('/search') and
            not r.sismember('visited', search_url))

def thread_crawl():
    while r.llen('url_stack'):
        url = r.rpop('url_stack').decode('utf-8')
        print(url)
        r.sadd('visited', url)
        if url.startswith(T_URL) and not r.sismember('tournament_urls', url):
            r.sadd('tournament_urls', url)
            with open("t_urls.txt" , "a") as f:
                f.write(url+'\n')
        try:
            req = urllib.request.urlopen(urljoin(BASE_URL, url))
        except:
            continue
        finally:
            r.rpop('url_stack')

        page = req.read()
        soup = BeautifulSoup(page, 'html.parser')
        for link in soup.find_all('a'):
            soup_url = link.get('href')
            if valid_search_url(soup_url):
                r.rpush('url_stack', soup_url)

r.rpush('url_stack', BASE_URL)
for i in range(NUM_THREADS):
    print("Starting thread " + str(i+1))
    threading.Thread(target=thread_crawl).start()
    time.sleep(1)
