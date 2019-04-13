import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
import re
import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.bassmaster.com/"
API_BASE_URL = "https://api.prod2.bassmasterdata.com/v1/data/final-results"

def get_json_body(scripts):
    start, text = 0, None
    for s in scripts:
        if s.text.startswith('jQuery.extend(Drupal.settings, '):
            start = len('jQuery.extend(Drupal.settings, ')
            text = s.text
            break
    if not text:
        return text
    while text[start] != '{':
        start += 1
    stack = [text[start]]
    end = start + 1
    while stack and end < len(text):
        if stack[-1] == '{' and text[end] == '}':
            stack.pop()
        elif text[end] == '{':
            stack.append(text[end])
        end += 1
    return text[start:end]

with open('t_urls.txt', 'r') as f:
    urls = f.read().split('\n')
    for path in urls:
        # Open url
        try:
            r = urllib.request.urlopen(urljoin(BASE_URL, path))
        except:
            continue
        # Get tournament ID from Drupal.settings
        soup = BeautifulSoup(r.read(), 'html.parser')
        json_body = get_json_body(soup.find_all('script'))
        if json_body:
            obj = json.loads(json_body)
            if "bass_tournaments" in obj:
                print(path + ": " + obj["bass_tournaments"]["tms"])
        """
        # Get data from api
        try:
            r = urllib.request.urlopen(urljoin(API_BASE_URL, t_id))
        except:
            continue
        # Write to file
        with open(path[1:]+'.json', 'w') as t:
            t.write(r.read())
        """
