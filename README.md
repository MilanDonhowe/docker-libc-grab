# docker-libc-grab
Grab libc from a given docker image hash--no docker install needed!

## Usage
```python3
python3 -m pip install -r requirements.txt
python3 ./pull.py ubuntu@sha256:bbf3d1baa208b7649d1d0264ef7d522e1dc0deeeaaf6085bf8e4618867f03494
```
And libc.so.6 will be saved in your current working directory.

