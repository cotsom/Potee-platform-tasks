import sys

import requests
from bs4 import BeautifulSoup

host = sys.argv[1]
port = sys.argv[2]

def ping():
    r = requests.get(f"http://{host}:{port}", timeout=2)
    if r.status_code == 200:
        if r.text == "pong":
            return 1
    return 0

def getReps():
    #headers = {"Authorization" : "Basic ZG9ja2VyLWFkbTphZG1pbg=="}
    session = requests.Session()
    try:
        r = session.get(f"http://{host}:{port}/v2/_catalog")
    except:
        return 0

    if r.status_code != 404:
        return 1
    else: return 0



if __name__ == '__main__':
    print(getReps())