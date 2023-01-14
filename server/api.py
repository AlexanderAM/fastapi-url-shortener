from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from server.model import URLBase, URLInfo

import validators
import secrets
import string


app = FastAPI()

urls = {
    "1": {
        "url": "123",
        "target_url": "http://ya.ru",
        "clicks": 0
    },
    "2": {
        "url": "1234",
        "target_url": "http://vk.ru",
        "clicks": 0
    },
}


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f"URL '{request.url}' doesn't exist"
    raise HTTPException(status_code=404, detail=message)


def create_random_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key() -> str:
    key = create_random_key()
    try:
        while next(get_url(url=key)):
            key = create_random_key()
    except StopIteration:
        pass
    return key


def get_url(urls=urls, **keys):
    ki = keys.items()
    for i in urls:
        dt = urls[i]
        if all((dt[k] == v) for (k, v) in ki):
            yield dt


def get_key(d, value):
    for k, v in d.items():
        if v == value:
            return k


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    return {
        "message": "Welcome to my url shortener application, use the /docs route to proceed"
    }


@app.get("/url", tags=["URL"])
async def list_urls():
    return urls


@app.get("/{url_key}", tags=["URL"])
async def forward_to_target_url(url_key: str, request: Request):
    try:
        if next(get_url(url=url_key)):
            next(get_url(url=url_key)).update({"clicks": next(get_url(url=url_key))["clicks"]+1})
            return RedirectResponse(next(get_url(url=url_key))['target_url'])
    except StopIteration:
        raise_not_found(request)


@app.post("/url", response_model=URLInfo, tags=["URL"])
async def create_url(url: URLBase):
    if not validators.url(url.target_url):
        raise_bad_request(message="Your provided URL is not valid")
    key = create_unique_random_key()
    urls[str(int(list(urls.keys())[-1]) + 1)] = {
        "url": key,
        "target_url": url.target_url,
        "clicks": 0
        }
    return next(get_url(target_url=url.target_url))


@app.delete("/url", tags=["URL"])
async def delete_url(url_key: str, request: Request):
    try:
        url = urls.pop(get_key(urls, next(get_url(url=url_key))))
        message = (
            f"Successfully deleted shortened URL for '{url['target_url']}'"
        )
        return {"detail": message}
    except StopIteration:
        raise_not_found(request)
