#!/usr/bin/env python
# -*- coding: utf-8 -*-
import functools
import hashlib
import io
from typing import Tuple

import httpx
from PIL import Image
from epicteller.core.config import Config


async def upload_image_from_url(url: str) -> Tuple[str, int, int]:
    image_data = await download_image(url)
    token, width, height = await upload_image(image_data)
    return token, width, height


async def download_image(url: str) -> bytes:
    async with httpx.AsyncClient() as http_client:
        r = await http_client.get(url)
        r.raise_for_status()
        return r.content


async def get_image_size(*, token: str = None, data: bytes = None) -> Tuple[int, int]:
    if not token and not data:
        raise ValueError
    if token:
        data = await download_image(get_full_url(token, size='r'))
    img = Image.open(io.BytesIO(data))
    return img.size


async def upload_image(image_data: bytes) -> Tuple[str, int, int]:
    digest = hashlib.md5(image_data).hexdigest()
    image_token = f"v1-{digest}"
    width, height = await get_image_size(data=image_data)
    async with httpx.AsyncClient() as http_client:
        r = await http_client.post(
            f"https://api.cloudflare.com/client/v4/accounts/{Config.CF_IMAGES_ACCOUNT_ID}/images/v1",
            headers={'Authorization': f'Bearer {Config.CF_IMAGES_API_KEY}'},
            data={'id': image_token},
            files={image_token: io.BytesIO(image_data)},
        )
        r.raise_for_status()
    return image_token, width, height


def get_full_url(token: str, size: str='hd') -> str:
    if not token:
        return ''
    return f"https://img.epicteller.com/cdn-cgi/imagedelivery/{Config.CF_IMAGES_ACCOUNT_HASH}/{token}/{size}"


get_avatar_url = functools.partial(get_full_url, size='xl')
