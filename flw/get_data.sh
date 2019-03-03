#!/bin/bash
# Initialize web session and XSRF token
wget -qO- --keep-session-cookies --save-cookies cookies.txt https://www.flwfishing.com/results

wget -qO- --load-cookies cookies.txt --header="cookie:we-love-cookies=1" --header="x-requested-with: XMLHttpRequest" --header="referer: https://www.flwfishing.com/results" https://www.flwfishing.com/ajax?method=getResults&cid=1&tyear=1997&tid=675&angler=pro
