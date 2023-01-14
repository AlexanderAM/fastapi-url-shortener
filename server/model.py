from pydantic import BaseModel
from typing import List


class URLBase(BaseModel):
    target_url: str


class URLInfo(URLBase):
    clicks: int
    url: str
