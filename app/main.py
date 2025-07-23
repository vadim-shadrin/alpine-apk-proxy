import os
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import requests

app = FastAPI()

ALPINE_MIRROR = os.getenv('ALPINE_MIRROR')
CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str) -> str:
    h = hashlib.sha256(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, h)

@app.get("/{path:path}")
async def proxy(request: Request, path: str):
    path = path.lstrip("/")
    target_url = f"{ALPINE_MIRROR}/{path}"
    cache_path = get_cache_path(target_url)

    if os.path.exists(cache_path):
        def file_iterator():
            with open(cache_path, "rb") as f:
                while chunk := f.read(8192):
                    yield chunk

        return StreamingResponse(file_iterator(), media_type="application/octet-stream")

    # download original
    r = requests.get(target_url, stream=True, timeout=10)
    if r.status_code != 200:
        return StreamingResponse(
            iter([b"Error: " + str(r.status_code).encode()]),
            status_code=r.status_code
        )

    # save to cache
    with open(cache_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    # give to client
    def file_iterator():
        with open(cache_path, "rb") as f:
            while chunk := f.read(8192):
                yield chunk

    return StreamingResponse(file_iterator(), media_type="application/octet-stream")


@app.get("/")
def index():
    return {
        "message": "Alpine Proxy is worked",
        "example": "Try /v3.22/main/x86_64/APKINDEX.tar.gz"
    }