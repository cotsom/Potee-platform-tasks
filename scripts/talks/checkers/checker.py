import random
import string
import sys
from bs4 import BeautifulSoup
import requests

def checker_name(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

host = sys.argv[1]
port = sys.argv[2]
schema = "http"
checker_name = checker_name(10)

def ping():
    r = requests.get(f"{schema}://{host}:{port}/", timeout=2)
    if r.status_code == 200:
        return 1
    return 0

def login():
    username = checker_name
    session = requests.Session()
    session.post(f"{schema}://{host}:{port}/",data={"login": username, "passwd": "q", "action": "signup"})
    session.post(f"{schema}://{host}:{port}", data={"login": username, "passwd": "q", "action": "signin"})
    print(session.cookies.get_dict())
    r = session.get(f"{schema}://{host}:{port}/talks")
    
    soup = BeautifulSoup(r.text, "lxml")
    req = soup.find("h1", class_="checker")
    if 'Potee' in req.text:
        return 1
    else: return 0

def favicon_availability():
    favicon = requests.get(f"{schema}://{host}:{port}/images?file=favicon.ico")
    if favicon.status_code == 200:
        return 1
    else: return 0

def not_found():
    payload = "checker_test"

    r = requests.get(f"{schema}://{host}:{port}/{payload}", timeout=2)
    
    soup = BeautifulSoup(r.text, "lxml")
    req = soup.find("h3")
    if payload in req.text:
        return 1
    return 0
    

if __name__ == '__main__':
    print(ping())
    print(login())
    print(favicon_availability())
    print(not_found())