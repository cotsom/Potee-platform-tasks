import random
import string
import subprocess
from bs4 import BeautifulSoup
import requests
from potee import ServiceBase

port = 5000
srv = ServiceBase()

manifest = {
   "schemaVersion": 2,
   "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
   "config": {
      "mediaType": "application/vnd.docker.container.image.v1+json",
      "size": 1472,
      "digest": "sha256:49176f190c7e9cdb51ac85ab6c6d5e4512352218190cd69b08e6fd803ffbf3da"
   },
   "layers": [
      {
         "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
         "size": 3370706,
         "digest": "sha256:c158987b05517b6f2c5913f3acef1f2182a32345a304fe357e3ace5fadcad715"
      }
   ]
}

def gen_tag(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@srv.ping
def ping(host):
    r = requests.get(f"http://{host}:{port}")
    if r.status_code == 200:
        return 'pong'

@srv.put("image")
def put_image(host, flag):
    _id = gen_tag()
    manifest['flag'] = flag
    headers = {'Content-Type': 'application/vnd.docker.distribution.manifest.v2+json'}
    r = requests.put(f'http://{host}:{port}/v2/alpine/manifests/{_id}', headers=headers, json=manifest)
    #TODO: answer check status
    #if r.status_code
    return _id

@srv.get("image")
def get_image(host, _id):
    headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    r = requests.get(f"http://{host}:{port}/v2/alpine/manifests/{_id}", headers=headers).json()
    return r.get("flag")
    
@srv.exploit("image")
def get_image(host):
    r = requests.get(f"http://{host}:{port}/v2/_catalog")
    if r.status_code == 200:
        return 1
    return 0

    
if __name__ == "__main__":
    srv.run()