import random
import string
import sys
from bs4 import BeautifulSoup
import requests
from potee import ServiceBase

port = 8001
schema = "http"
srv = ServiceBase()

def gen_password(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@srv.ping
def ping(host):
    r = requests.get(f"{schema}://{host}:{port}/", timeout=2)
    if r.status_code == 200:
        return 'pong'

@srv.put("auth")
def login(host, flag):
    username = flag
    print(flag)
    password = gen_password(5)
    session = requests.Session()
    session.post(f"{schema}://{host}:{port}/",data={"login": username, "passwd": password, "action": "signup"})
    print(session.cookies.get_dict()['session'])
    return session.cookies.get_dict()['session']

@srv.get('auth')
def login(host, session):
    s = requests.Session() 
    s.cookies.set("session", session)
    r = session.get(f"{schema}://{host}:{port}/talks")
    
    soup = BeautifulSoup(r.text, "lxml")
    req = soup.find("h1", class_="checker")
    if 'Potee' in req.text:
        return 1
    else: return 0
    
if __name__ == "__main__":
    srv.run()