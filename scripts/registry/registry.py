import subprocess
from bs4 import BeautifulSoup
import requests
from potee import ServiceBase

port = 5000
srv = ServiceBase()



@srv.ping
def ping(host):
    r = requests.get(f"http://{host}:{port}")
    if r.status_code == 200:
        return 'pong'

@srv.put("image")
def put_image(host, flag):
    tag_image = f'tag alpine {host}:{port}/{flag}'
    push_image = f'push {host}:{port}/{flag}'
    subprocess.call(["docker", "tag", "alpine", f'{host}:{port}/{flag}'], stdout=subprocess.DEVNULL)
    subprocess.call(["docker", "push", f'{host}:{port}/{flag}'], stdout=subprocess.DEVNULL)
    return flag

@srv.get("image")
def get_image(host, id):
    r = requests.get(f"http://{host}:{port}/v2/_catalog")
    if f"\"{id}\"" in r.text:
        return 1
    return 0
    
@srv.exploit("image")
def get_image(host):
    r = requests.get(f"http://{host}:{port}/v2/_catalog")
    if r.status_code == 200:
        return 1
    return 0

    
if __name__ == "__main__":
    srv.run()