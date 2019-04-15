import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
import re
import json
from bs4 import BeautifulSoup

BASE_URL = "https://www.bassmaster.com/"
API_BASE_URL = "https://api.prod2.bassmasterdata.com/v1/data/final-results/"
PRO_OR_CO = ("co", "pro")

def parse_json_body(scripts):
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

def extract_tournament_id(s):
    # Get tournament ID from Drupal.settings
    json_body = parse_json_body(s.find_all('script'))
    if json_body:
        obj = json.loads(json_body)
        if "bass_tournaments" in obj:
            return obj["bass_tournaments"]["tms"]
    return None

def extract_tournament_name(s):
    title = s.find(id="page-title")
    if title:
        return '_'.join(
            [t for t in title.get_text()
            .replace('\n','')
            .replace('\\','')
            .replace('/', '')
            .split(' ') if t])
    return None

with open('t_urls.txt', 'r') as f:
    urls = f.read().split('\n')
    for path in urls:
        # Open url
        try:
            r = urllib.request.urlopen(urljoin(BASE_URL, path))
        except:
            print("Bad url: " + urljoin(BASE_URL, path))
            continue

        soup = BeautifulSoup(r.read(), 'html.parser')
        t_name = extract_tournament_name(soup)
        t_id = extract_tournament_id(soup)

        if not t_id:
            continue

        t_dict = {}
        if t_name:
            t_dict["name"] = t_name

        # Get data from api
        for poc in range(2):
            # Get final results
            try:
                r = urllib.request.urlopen(urljoin(API_BASE_URL, t_id + '/' + str(poc)))
            except:
                print("Bad url: " + urljoin(API_BASE_URL, t_id + '/' + str(poc)))
                continue
            t_dict[PRO_OR_CO[poc]] = {}
            try:
                final_results = json.loads(r.read())
                if final_results:
                    t_dict[PRO_OR_CO[poc]]["final"] = final_results
            except:
                print("Couldn't parse reults for " +urljoin(API_BASE_URL, t_id + '/' + str(poc)))
            # Get results for individual days
            for day in range(1, 5):
                try:
                    r = urllib.request.urlopen(urljoin(API_BASE_URL, t_id + '/' + str(poc) + '/' + str(day)))
                except:
                    print("Couldn't parse reults for " +urljoin(API_BASE_URL, t_id + '/' + str(poc) + '/' + str(day)))
                    continue
                try:
                    day_results = json.loads(r.read())
                    if day_results:
                        t_dict[PRO_OR_CO[poc]]["day_"+str(day)] = day_results
                except:
                    print("Couldn't parse reults for " +urljoin(API_BASE_URL, t_id + '/' + str(poc) + '/' + day))
                    continue

                # Store tournament data
                if t_name:
                    with open(t_name +'.json', 'w') as t:
                        t.write(json.dumps(t_dict))
                    continue
                with open(str(t_id) +'.json', 'w') as t:
                    t.write(json.dumps(t_dict))
