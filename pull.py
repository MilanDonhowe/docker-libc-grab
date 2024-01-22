from requests import *
import tarfile
import os
import click
import io

@click.command()
@click.option('-d', '--digest', help="image digest in the format of <image>@<digest>")
def grabLibc(digest):
    """Automatically extracts the libc.so.6 file from a given container image hash."""
    if digest == None:
        print("[*] No docker image digest provided...")
        return
    name, digest = digest.split('@')

    print("[*] Acquiring auth token from docker.io...")
    # Grab Auth token
    auth = get("https://auth.docker.io/token", params={
        "service":"registry.docker.io",
        "scope":f"repository:library/{name}:pull"
    }).json()
    token = auth['token']

    print("[*] Downloading manifest for docker image...")
    # Grab manifest
    manifest = get(f"https://registry-1.docker.io/v2/library/{name}/manifests/{digest}" ,headers={
        'Authorization': f'Bearer {token}',
        'Accept':'application/vnd.oci.image.manifest.v1+json'
    }).json()

    print(f"[*] Found manifest with {len(manifest['layers'])} layers")
    # Download all layers, find libc.so.6
    candidate_libcs = []
    for i, layer in enumerate(manifest['layers']):
        print(f"[*] Searching for libc file in layer {i+1}...")
        blob = get(f"https://registry-1.docker.io/v2/library/{name}/blobs/{layer['digest']}" ,headers={
            'Authorization': f'Bearer {token}'
        }, stream=True)
        # for now, just do a grep search for libc.so.6--it's probably the right libc
        # I'll need to do more research on a smarter way to acquire the libc in the future
        
        # look for libc.so.6
        with tarfile.open(fileobj=io.BytesIO(blob.content), mode='r:gz') as blob_tar:
            search_results = list(filter(lambda x: 'libc.so.6' in x.name, blob_tar.getmembers()))
            for result in search_results:
                candidate_libcs.append(blob_tar.extractfile(result).read())

    print(f"[*] found {len(candidate_libcs)} possible libc files")
    # just take the libc.so.6
    if len(candidate_libcs) > 0:
        with open('libc.so.6', "wb+") as libc:
            libc.write(candidate_libcs[0])
        print("[*] Saved libc as ./libc.so.6")
if __name__ == '__main__':
    grabLibc()


