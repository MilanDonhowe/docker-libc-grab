from requests import *
import tarfile
import os
from sys import argv

# command line handling
if len(argv) > 1:
    image = argv[1]

#image='ubuntu@sha256:bbf3d1baa208b7649d1d0264ef7d522e1dc0deeeaaf6085bf8e4618867f03494'
name, digest = image.split('@')


def getAuth(image):
    """Grabs auth token for docker registry"""
    response = get("https://auth.docker.io/token", params={
        "service":"registry.docker.io",
        "scope":f"repository:library/{image}:pull"
    })
    if (response.status_code == 200):
        return response.json()
    raise ConnectionRefusedError("Could not get Authenticated")

auth = getAuth(name)
token = auth['token']

# Grab manifest
manifest = get(f"https://registry-1.docker.io/v2/library/{name}/manifests/{digest}" ,headers={
    'Authorization': f'Bearer {token}',
    'Accept':'application/vnd.oci.image.manifest.v1+json'
}).json()

# Grab Layer
layer = get(f"https://registry-1.docker.io/v2/library/{name}/blobs/{manifest['layers'][0]['digest']}" ,headers={
    'Authorization': f'Bearer {token}'
}, stream=True)


# Download tar
with open('layer.tar', 'wb') as f:
    f.write(layer.content)
# Grab libc
with tarfile.open('layer.tar', "r:gz") as file:
    libc_tarinfo = list(filter(lambda x: 'libc.so.6' in x.name, file.getmembers()))[0]
    libc_data = file.extractfile(libc_tarinfo).read()
with open("libc.so.6", "wb") as libc:
    libc.write(libc_data)
# Remove Layer
os.remove('layer.tar')
