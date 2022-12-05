import sys
from bs4 import BeautifulSoup
import requests
import random
import string

def checker_name(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

host = sys.argv[1]
port = sys.argv[2]
schema = "http"
username = checker_name(10)

def ping():
    r = requests.get(f"{schema}://{host}:{port}/", timeout=2)
    if r.status_code == 200:
        return 1
    return 0

def login():
    session = requests.Session()
    session.post(f"{schema}://{host}:{port}/",data={"login": username, "passwd": "q", "action": "signup"})
    session.post(f"{schema}://{host}:{port}", data={"login": username, "passwd": "q", "action": "signin"})
    r = session.get(f"{schema}://{host}:{port}/shop")
    
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("li", class_="tag")
    return req.text
    
def buy():
    session = requests.Session()
    session.post(f"{schema}://{host}:{port}", data={"login": username, "passwd": "q", "action": "signin"})
    r = session.post(f"{schema}://{host}:{port}/shop", data={"product-id": 1})
    r = session.get(f"{schema}://{host}:{port}/inventory")
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("a", {"class" : 'product'})
    session.get(f"{schema}://{host}:{port}/delete")
    if req.text == 'Krysa':
        return 1
    else: return 0
    # for i in req:
    #     print(i.text)
    #     if req.text == "Krysa":
    #         return 1
    # return 0
    

if __name__ == '__main__':
    print(login())
    print(buy())